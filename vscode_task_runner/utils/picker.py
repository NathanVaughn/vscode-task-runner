from __future__ import annotations

import os
from typing import TYPE_CHECKING, Optional

import questionary

from vscode_task_runner.exceptions import (
    BadInputEnvironmentVariable,
    ResponseNotProvided,
)

if TYPE_CHECKING:
    from vscode_task_runner.models.tasks import Task  # pragma: no cover


def check_item_with_options(env_value: str, options: list[str]) -> None:
    """
    Given an environment variable value, check if it matches any of the options.
    Otherwise, raise an exception.
    """
    if env_value not in options:
        raise BadInputEnvironmentVariable(
            f"Input {env_value} does not match any potential options: {', '.join(options)}"
        )


def determine_default_build_task(tasks: list[Task]) -> Optional[Task]:
    """
    Given a list of potential tasks, return the default build task.
    """
    task_labels = [task.label for task in tasks]

    # allow the user to provide the input value via environment variable
    if env_value := os.environ.get("VTR_DEFAULT_BUILD_TASK"):
        # ensure the environment variable matches one of the tasks
        check_item_with_options(env_value, task_labels)

        # match task label to task object
        # just use the first item in the list, they all have a reference
        # to the parent tasks object. We will always receive a list with at least
        # two tasks
        return tasks[0]._tasks.tasks_dict[env_value]

    # otherwise, obtain from user input
    question = questionary.select(
        "Select the default build task",
        choices=task_labels,
    )

    output: Optional[str] = question.ask()
    if output is None:
        raise ResponseNotProvided("No response provided")  # pragma: no cover

    return tasks[0]._tasks.tasks_dict[output]
