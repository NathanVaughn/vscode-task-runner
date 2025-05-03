import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

from vscode_task_runner import printer
from vscode_task_runner.exceptions import MissingCommand, WorkingDirectoryNotFound
from vscode_task_runner.models.enums import TaskTypeEnum
from vscode_task_runner.models.execution_level import ExecutionLevel
from vscode_task_runner.models.shell import ShellConfiguration
from vscode_task_runner.models.strings import CommandStringConfig, csc_value
from vscode_task_runner.models.task import DependsOrderEnum, Task
from vscode_task_runner.utils.paths import which_resolver
from vscode_task_runner.utils.shell import get_parent_shell
from vscode_task_runner.utils.strings import joiner
from vscode_task_runner.vscode import task_configuration, terminal_task_system


def _new_task_env(task: Task) -> dict[str, str]:
    """
    Given a task, return the environment variables to set.
    """

    # VSCode will merge environment variables for os-independent options
    # and os-specific options. It will not merge the environment variables
    # from the global configuration to the task-specific configuration.
    # if the task defines options.

    global_tasks_env = task._tasks.new_env_os()
    task_env = task.new_env_os()

    # if the task defined any of its own options, discard global
    # otherwise, return the global task environment
    return task_env or global_tasks_env


def task_env(task: Task) -> dict[str, str]:
    """
    Given a task, return the environment variables to set.
    """
    task_env = _new_task_env(task)
    # combine with a copy of the current environment
    return {**os.environ.copy(), **task_env}


def task_cwd(task: Task) -> Path:
    """
    Given a task, return the current working directory.
    """
    cwd = Path(os.getcwd())

    # vscode treats cwd as an absolute path
    # this works as well on windows to define the root directory
    # this still works because an absolute joined to an absolute path
    # will yield the joined absolute path
    # pathlib.Path("/tmp").joinpath("/var") -> Path("/var/")
    base = Path("/")

    # task settings
    if task_cwd := task.cwd_os():
        cwd = base.joinpath(task_cwd)

    # global settings
    elif global_cwd := task._tasks.cwd_os():
        cwd = base.joinpath(global_cwd)

    if not cwd.is_dir():
        raise WorkingDirectoryNotFound(f"Working directory {cwd} does not exist")

    return cwd


def task_command(task: Task) -> Optional[CommandStringConfig]:
    """
    Given a task, return the command.
    """
    command = None

    # task settings
    if task_command := task.command_os():
        command = task_command

    # global settings
    elif global_command := task._tasks.command_os():
        command = global_command

    return command


def task_args(task: Task) -> list[CommandStringConfig]:
    """
    Given a task, return the arguments to pass to the command.
    """
    global_args = task._tasks.args_os()
    task_args = task.args_os()

    # in the case that there is a global command defined, but not a task
    # command, tack on the task args to the global args
    task_command = task.command_os()
    return global_args + task_args if task_command is None else task_args


def task_shell(task: Task) -> ShellConfiguration:
    """
    Given a task, return the current shell configuration.
    """
    shell = ShellConfiguration()

    # task settings
    if task_shell := task.shell_os():
        shell = task_shell

    # global settings
    elif global_shell := task._tasks.shell_os():
        shell = global_shell

    if not shell.executable:
        # if no shell binary defined, use the parent shell
        shell = get_parent_shell()

    # make sure shell executable exists and is absolute
    assert shell.executable is not None
    shell.executable = which_resolver(shell.executable)

    # return the shell config
    return shell


def is_virtual_task(task: Task) -> bool:
    """
    Returns if a task is a virtual task. This is the case
    if the task does not define a command, and depends on other tasks
    """
    return not bool(task_command(task)) and bool(task.depends_on)


def task_subprocess_command(
    task: Task, extra_args: Optional[list[str]] = None
) -> list[str]:
    """
    Given a task and extra arguments, return the command to run the task.
    """
    # deal with mutable defaults
    if extra_args is None:
        extra_args = []

    command = task_command(task)
    if command is None:
        raise MissingCommand(f"Task '{task.label}' does not define a command")

    args = task_args(task)

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
        shell_config = task_shell(task)

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
            cmd,
            shell=False,
            cwd=task_cwd(task),
            env=task_env(task),
            stdout=sys.stdout,
            stderr=sys.stderr,
        )

        if proc.returncode != 0:
            printer.error(
                f"Task {printer.yellow(task.label)} returned with exit code {proc.returncode}"
            )
            sys.exit(proc.returncode)
