import subprocess
import sys
from typing import Optional

from vscode_task_runner import printer
from vscode_task_runner.exceptions import MissingCommand
from vscode_task_runner.models.enums import TaskTypeEnum
from vscode_task_runner.models.execution_level import ExecutionLevel
from vscode_task_runner.models.strings import csc_value
from vscode_task_runner.models.task import DependsOrderEnum, Task
from vscode_task_runner.utils.paths import which_resolver
from vscode_task_runner.utils.strings import joiner
from vscode_task_runner.vscode import task_configuration, terminal_task_system


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


def execute_tasks(tasks: list[Task], extra_args: list[str]) -> None:
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

    # iterate through all tasks
    index = 0
    for level in levels:
        for task in level.tasks:
            index += 1

            # only add extra args to last task
            # since this function won't get extra args when more than one
            # top level tasks are run
            execute_extra_args = []
            if index == task_count:
                execute_extra_args = extra_args

            execute_task(
                task, index=index, total=task_count, extra_args=execute_extra_args
            )


def execute_task(task: Task, index: int, total: int, extra_args: list[str]) -> None:
    """
    Actually execute the task. Takes the task object, current index, total number,
    and any extra args.
    """
    if is_virtual_task(task):
        printer.info(
            f"[{index}/{total}] Task {printer.yellow(task.label)} has no direct command to execute"
        )
        return

    cmd = task_subprocess_command(task, extra_args=extra_args)

    with printer.group(f"Task {task.label}"):
        printer.info(
            f"[{index}/{total}] Executing task {printer.yellow(task.label)}: {printer.blue(joiner(cmd))}"
        )
        proc = subprocess.run(
            args=cmd,
            shell=False,
            cwd=task.cwd_use(),
            env=task.env_use(),
            stdout=sys.stdout,
            stderr=sys.stderr,
        )

        if proc.returncode != 0:
            printer.error(
                f"Task {printer.yellow(task.label)} returned with exit code {proc.returncode}"
            )
            sys.exit(proc.returncode)
