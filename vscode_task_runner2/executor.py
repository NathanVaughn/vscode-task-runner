import os
from pathlib import Path
from typing import Optional

from vscode_task_runner2.models.execution_level import ExecutionLevel
from vscode_task_runner2.models.task import DependsOrderEnum, Task


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


def _new_task_env(task: Task) -> dict[str, str]:
    """
    Given a task, return the environment variables to set.
    """

    # VSCode will merge environment variables for os-independent options
    # and os-specific options. It will not merge the environment variables
    # from the global configuration to the task-specific configuration.
    # if the task defines options.

    global_tasks_env = {}
    task_env = {}

    if task._tasks.options:
        global_tasks_env = {**global_tasks_env, **task._tasks.options.env}
    if task._tasks.os and task._tasks.os.options:
        global_tasks_env = {**global_tasks_env, **task._tasks.os.options.env}

    if task.options:
        task_env = {**task_env, **task.options.env}
    if task.os and task.os.options:
        task_env = {**task_env, **task.os.options.env}

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

    # try global settings first
    if task._tasks.options and task._tasks.options.cwd:
        cwd = base.joinpath(task._tasks.options.cwd)
    if task._tasks.os and task._tasks.os.options and task._tasks.os.options.cwd:
        cwd = base.joinpath(task._tasks.os.options.cwd)
    # then task settings
    if task.options and task.options.cwd:
        cwd = base.joinpath(task.options.cwd)
    if task.os and task.os.options and task.os.options.cwd:
        cwd = base.joinpath(task.os.options.cwd)

    return cwd


def task_command(task: Task) -> Optional[str]:
    """
    Given a task, return the current working directory.
    """
    command = None

    # try global settings first
    if task._tasks.command:
        command = task._tasks.command
    if task._tasks.os and task._tasks.os.command:
        command = task._tasks.os.command
    # then task settings
    if task.command:
        command = task.command
    if task.os and task.os.command:
        command = task.os.command

    return command  # type: ignore


def task_subprocess_command(task: Task, extra_args: list[str]) -> list[str]:
    """
    Given a task and extra arguments, return the command to run the task.
    """
    return []


def execute_tasks(tasks: list[Task], extra_args: list[str]) -> None:
    """
    Execute the tasks in the order they are defined in the tasks.json file.
    """
    # collect all tasks to execute
    collect_levels(tasks)
