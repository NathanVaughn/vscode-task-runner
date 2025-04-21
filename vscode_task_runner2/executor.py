import os
from pathlib import Path
from typing import Optional

from vscode_task_runner2.models.config import CommandString, ShellConfiguration
from vscode_task_runner2.models.enums import TaskType
from vscode_task_runner2.models.execution_level import ExecutionLevel
from vscode_task_runner2.models.task import DependsOrder, Task
from vscode_task_runner2.utils.paths import which_resolver
from vscode_task_runner2.utils.shell import get_parent_shell


def _new_task_env(task: Task) -> dict[str, str]:
    """
    Given a task, return the environment variables to set.
    """

    # VSCode will merge environment variables for os-independent options
    # and os-specific options. It will not merge the environment variables
    # from the global configuration to the task-specific configuration.
    # if the task defines options.

    global_tasks_env = task._tasks.new_env_computed()
    task_env = task.new_env_computed()

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
    if task_cwd := task.cwd_computed():
        cwd = base.joinpath(task_cwd)

    # global settings
    elif global_cwd := task._tasks.cwd_computed():
        cwd = base.joinpath(global_cwd)

    return cwd


def task_command(task: Task) -> Optional[CommandString]:
    """
    Given a task, return the current working directory.
    """
    command = None

    # task settings
    if task_command := task.command_computed():
        command = task_command

    # global settings
    elif global_command := task._tasks.command_computed():
        command = global_command

    # convert the various string types to a CommandString
    return command


def task_args(task: Task) -> list[CommandString]:
    """
    Given a task, return the arguments to pass to the command.
    """
    global_args = task._tasks.args_computed()
    task_args = task.args_computed()

    # in the case that there is a global command defined, but not a task
    # command, tack on the task args to the global args
    task_command = task.command_computed()
    return global_args + task_args if task_command is None else task_args


def task_shell(task: Task) -> ShellConfiguration:
    """
    Given a task, return the current shell configuration.
    """
    shell = ShellConfiguration()

    # task settings
    if task_shell := task.shell_computed():
        shell = task_shell

    # global settings
    elif global_shell := task._tasks.shell_computed():
        shell = global_shell

    if not shell.executable:
        # if no shell binary defined, use the parent shell
        shell = get_parent_shell()

    # make sure shell executable exists and is absolute
    assert shell.executable is not None
    shell.executable = which_resolver(shell.executable)

    # return the shell config
    return shell


def task_subprocess_command(
    task: Task, extra_args: Optional[list[str]] = None
) -> list[str]:
    """
    Given a task and extra arguments, return the command to run the task.
    """
    if extra_args is None:
        extra_args = []

    if task.type_enum == TaskType.process:
        command = task_command(task)

        subprocess_command = [which_resolver(command)]
        for arg in task_args(task) + extra_args:
            # the args must be strings too
            subprocess_command.append(arg)

        return subprocess_command

    elif task.type_enum == TaskType.shell:
        shell_config = task_shell(task)

        if shell_config.args is None:
            shell_config.args = []

        # build the shell quoting options
        vscode_task_runner2.terminal_task_system.get_quoting_options(
            shell_type, shell_config
        )
        assert shell_config.quoting is not None

        # figure out how to tack on extra args
        command = self.command
        assert command is not None
        args = self.args

        if extra_args:
            # if we have args, tack it on to that
            if args:
                args = args + extra_args
            else:
                # if we only have a command, tack it on to that
                extra_text = " " + " ".join(extra_args)

                if isinstance(command, str):
                    command += extra_text
                else:
                    command.value += extra_text

        return [
            shell_config.executable
        ] + vscode_task_runner2.terminal_task_system.create_shell_launch_config(
            shell_type,
            shell_config.args,
            vscode_task_runner2.terminal_task_system.build_shell_command_line(
                shell_type,
                shell_config.quoting,
                command,
                args,
            ),
        )


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

    # Add the current task to the execution levels
    execution_levels.append(ExecutionLevel(order=DependsOrder.sequence, tasks=[task]))
    return execution_levels


def execute_tasks(tasks: list[Task], extra_args: list[str]) -> None:
    """
    Execute the tasks in the order they are defined in the tasks.json file.
    """
    # collect all tasks to execute
    collect_levels(tasks)
