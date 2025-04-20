import os
from pathlib import Path
from typing import Optional

from vscode_task_runner2.models.execution_level import ExecutionLevel
from vscode_task_runner2.models.options import CommandString
from vscode_task_runner2.models.task import DependsOrderEnum, Task


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
    return command.export_command_string() if command else None


def task_args(task: Task) -> list[CommandString]:
    """
    Given a task, return the arguments to pass to the command.
    """
    global_args = task._tasks.args_computed()
    task_args = task.args_computed()

    # in the case that the command defined globally and in the task are the same,
    # tack on additional args
    task_command = task.command_computed()
    global_command = task._tasks.command_computed()

    print(task_command, task_args)
    print(global_command, global_args)

    # if the task does not have a command,
    # combine with global args
    return global_args + task_args if task_command is None else task_args


def task_subprocess_command(task: Task, extra_args: list[str]) -> list[str]:
    """
    Given a task and extra arguments, return the command to run the task.
    """
    return []


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
    execution_levels.append(
        ExecutionLevel(order=DependsOrderEnum.sequence, tasks=[task])
    )
    return execution_levels


def execute_tasks(tasks: list[Task], extra_args: list[str]) -> None:
    """
    Execute the tasks in the order they are defined in the tasks.json file.
    """
    # collect all tasks to execute
    collect_levels(tasks)
