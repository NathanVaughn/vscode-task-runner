import concurrent.futures
import os
import queue
import subprocess
import sys
import threading
from typing import NamedTuple, Optional, TextIO

from vscode_task_runner import printer
from vscode_task_runner.exceptions import MissingCommand
from vscode_task_runner.models.enums import (
    OutputStreamEnum,
    TaskExecutionStateEnum,
    TaskTypeEnum,
)
from vscode_task_runner.models.execution_level import ExecutionLevel
from vscode_task_runner.models.strings import csc_value
from vscode_task_runner.models.task import DependsOrderEnum, Task
from vscode_task_runner.utils.paths import which_resolver
from vscode_task_runner.utils.strings import joiner
from vscode_task_runner.vscode import task_configuration, terminal_task_system


class OutputLine(NamedTuple):
    text: str
    stream: OutputStreamEnum


def is_virtual_task(task: Task) -> bool:
    """
    Returns if a task is a virtual task. This is the case
    if the task does not define a command, and depends on other tasks
    """
    return not bool(task.command_use()) and bool(task.depends_on)


def task_subprocess_command(
    task: Task, extra_args: Optional[list[str]] = None
) -> list[str]:
    """
    Given a task and extra arguments, return the command to run the task.
    """
    # deal with mutable defaults
    if extra_args is None:
        extra_args = []

    command = task.command_use()
    if command is None:
        raise MissingCommand(f"Task '{task.label}' does not define a command")

    args = task.args_use()

    if task.type_enum == TaskTypeEnum.process:
        # turn into raw string
        command_value = csc_value(command)

        # resolve to a path
        subprocess_command = [which_resolver(command_value)]

        # convert the args into string as well
        subprocess_command.extend(csc_value(arg) for arg in args + extra_args)

        return subprocess_command

    elif task.type_enum == TaskTypeEnum.shell:
        # shell conversion
        command = task_configuration.shell_string(command)
        args = [task_configuration.shell_string(arg) for arg in args]

        # figure out shell config
        shell_config = task.shell_use()

        # build the shell quoting options
        shell_config.quoting = terminal_task_system.get_quoting_options(shell_config)

        # figure out how to tack on extra args
        if extra_args:
            # if we have args, tack it on to that
            if args:
                args = args + extra_args
            else:
                # if we only have a command, tack it on to that
                extra_text = " " + joiner(extra_args)

                if isinstance(command, str):
                    command += extra_text
                else:
                    command.value += extra_text

        # no situation in which shell executable is not set by this point
        shell_executable = shell_config.executable
        assert shell_executable is not None

        return [shell_executable] + terminal_task_system.create_shell_launch_config(
            shell_config,
            terminal_task_system.build_shell_command_line(
                shell_type=shell_config.type_,
                shell_quoting_options=shell_config.quoting,
                command=command,
                args=args,
            ),
        )
    else:
        # will be caught earlier
        return []  # pragma: nocover


def collect_levels(tasks: list[Task]) -> list[ExecutionLevel]:
    """
    Given a list of task labels, return the task and all child tasks, recursively.
    """
    execution_levels: list[ExecutionLevel] = []

    for task in tasks:
        execution_levels.extend(_collect_levels_recursive(task))

    return execution_levels


def _collect_levels_recursive(task: Task) -> list[ExecutionLevel]:
    """
    Given a task label, return the task and all child tasks, recursively.
    """
    execution_levels: list[ExecutionLevel] = []

    def _walk_tree(tree_task: Task) -> None:
        child_tasks = tree_task.depends_on

        # depth first search
        for child_task in child_tasks:
            _walk_tree(child_task)

        # add an execution level for the current task
        if child_tasks:
            execution_levels.append(
                ExecutionLevel(order=tree_task.depends_order, tasks=child_tasks)
            )

    _walk_tree(task)

    # Add the current task to the execution levels
    execution_levels.append(
        ExecutionLevel(order=DependsOrderEnum.sequence, tasks=[task])
    )
    return execution_levels


def execute_tasks(tasks: list[Task], extra_args: list[str]) -> int:
    """
    Execute the tasks in the order they are defined in the tasks.json file.
    """
    # collect all tasks to execute
    levels = collect_levels(tasks)

    # ensure all tasks are supported
    for level in levels:
        for task in level.tasks:
            if not task.is_supported():
                printer.error(f"Task {printer.yellow(task.label)} is not supported")
                sys.exit(1)

    # resolve all variables in all tasks
    # and count all
    task_count = len(
        [task.resolve_variables() for level in levels for task in level.tasks]
    )

    # track task results
    completed: list[str] = []
    failed: list[str] = []

    def should_continue(task: Task) -> bool:
        """
        Process the results of a task execution. If a task fails and
        VTR_CONTINUE_ON_ERROR is not set, exit immediately.

        This returns whether or not to continue execution.
        """
        # track results
        if task._execution_returncode == 0:
            completed.append(task.label)

        else:
            failed.append(task.label)

            if not os.environ.get("VTR_CONTINUE_ON_ERROR"):
                # exit immediately
                printer.summary(
                    completed_tasks=completed,
                    # this is the only situation where we have skipped tasks
                    skipped_tasks=[
                        task.label
                        for level in levels
                        for task in level.tasks
                        if task._execution_state == TaskExecutionStateEnum.pending
                    ],
                    failed_tasks=failed,
                )

                return False

        return True

    # this keeps track of which task we are on
    # for the sake of extra args and printing
    index = 0

    # iterate through all tasks
    for level in levels:
        if level.order == DependsOrderEnum.parallel:
            # parallel execution
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = []

                for task in level.tasks:
                    index += 1

                    # only add extra args to last task
                    # since this function won't get extra args when more than one
                    # top level tasks are run
                    execute_extra_args = extra_args if index == task_count else []

                    # submit the task to the executor
                    futures.append(
                        executor.submit(
                            execute_task,
                            task,
                            index,
                            task_count,
                            True,
                            execute_extra_args,
                        )
                    )

                # this actually executes the tasks
                [f.result() for f in futures]

                for task in level.tasks:
                    if not should_continue(task):
                        return task._execution_returncode

        else:
            # sequential execution
            for task in level.tasks:
                index += 1

                # only add extra args to last task
                # since this function won't get extra args when more than one
                # top level tasks are run
                execute_extra_args = extra_args if index == task_count else []

                execute_task(
                    task,
                    index=index,
                    total=task_count,
                    parallel=False,
                    extra_args=execute_extra_args,
                )

                if not should_continue(task):
                    return task._execution_returncode

    # this is reached if all tasks completed successfully or continue on error is set
    # to True
    printer.summary(completed_tasks=completed, skipped_tasks=[], failed_tasks=failed)
    return int(bool(failed))


def execute_task(
    task: Task, index: int, total: int, parallel: bool, extra_args: list[str]
) -> int:
    """
    Actually execute the task. Takes the task object, current index, total number,
    whether this is a parallel task, and any extra args.

    Returns the exit code of the task.
    """
    if is_virtual_task(task):
        printer.info(
            f"[{index}/{total}] Task {printer.yellow(task.label)} has no direct command to execute"
        )
        return 0

    cmd = task_subprocess_command(task, extra_args=extra_args)

    def run_cmd() -> int:
        printer.info(
            f"[{index}/{total}] Executing task {printer.yellow(task.label)}: {printer.blue(joiner(cmd))}"
        )

        # in parallel mode, we want to provide a prefix to each line
        # so we need to pipe in the subprocess output
        proc = subprocess.Popen(
            args=cmd,
            shell=False,
            cwd=task.cwd_use(),
            env=task.env_use(),
            stdout=subprocess.PIPE if parallel else sys.stdout,
            stderr=subprocess.PIPE if parallel else sys.stderr,
            text=True,
            bufsize=1,
        )

        # if not running in parallel, we can just wait
        # for the process to finish
        if not parallel:
            proc.wait()

        else:
            # https://stackoverflow.com/a/18423003
            # https://stackoverflow.com/a/17190793
            # create a queue to store output lines
            q: queue.Queue[Optional[OutputLine]] = queue.Queue()

            def read_stream(pipe: TextIO, stream: OutputStreamEnum) -> None:
                """
                This function will continously try to read lines
                from a stream, and put them in our output queue. Once
                the stream is empty, it will close.
                """
                for line in iter(pipe.readline, ""):
                    q.put(
                        OutputLine(
                            text=f"[{printer.yellow(task.label)}] {line.rstrip()}",
                            stream=stream,
                        )
                    )
                pipe.close()

            def print_output() -> None:
                """
                This will try to get items from the queue and print them out.
                Once an item in the queue that is simply a None, it will exit.
                """
                for output_line in iter(q.get, None):
                    if output_line.stream == OutputStreamEnum.stdout:
                        printer.stdout(output_line.text)
                    elif output_line.stream == OutputStreamEnum.stderr:
                        printer.stderr(output_line.text)

            # start the threads
            t_stdout = threading.Thread(
                target=read_stream, args=(proc.stdout, OutputStreamEnum.stdout)
            )
            t_stderr = threading.Thread(
                target=read_stream, args=(proc.stderr, OutputStreamEnum.stderr)
            )
            t_print = threading.Thread(target=print_output)

            for t in {t_stdout, t_stderr, t_print}:
                t.start()

            # wait for the proces to finish
            proc.wait()

            # wait for the reader threads to finish
            for t in {t_stdout, t_stderr}:
                t.join()

            # tell the output thread to stop
            q.put(None)

            # wait for the output thread to finish
            t_print.join()

        # update task execution state
        task._execution_returncode = proc.returncode

        # handle the two outcomes
        if task._execution_returncode != 0:
            task._execution_state = TaskExecutionStateEnum.failed

            # warning output if failed
            printer.error(
                f"Task {printer.yellow(task.label)} returned with exit code {proc.returncode}"
            )
        else:
            task._execution_state = TaskExecutionStateEnum.completed

        return task._execution_returncode

    # if we have more than one task, group the output
    if total > 1:
        with printer.group(f"Task {task.label}"):
            return run_cmd()
    else:
        return run_cmd()
