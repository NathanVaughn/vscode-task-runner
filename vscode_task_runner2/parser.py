import os
from typing import TYPE_CHECKING

import pydantic
import pyjson5

from vscode_task_runner2.constants import TASKS_FILE
from vscode_task_runner2.exceptions import TasksFileInvalid, TasksFileNotFound
from vscode_task_runner2.models.tasks import Tasks

if TYPE_CHECKING:
    from vscode_task_runner2.models.input import Input

RUNTIME_VARIABLES: dict[str, str] = {}
INPUTS: dict[str, Input] = {}


def load_vscode_json(path: str) -> dict:
    """
    Given a working directory, loads the vscode tasks config.
    """
    tasks_json = os.path.join(path, TASKS_FILE)

    if not os.path.isfile(tasks_json):
        raise TasksFileNotFound(f"Tasks file not found at {tasks_json}")

    with open(tasks_json, "r") as fp:
        # use pyjson 5 to deal with comments and other bad syntax
        return pyjson5.decode(fp.read())


def load_tasks(path: str = os.getcwd()) -> Tasks:
    """
    Load the model from the tasks.json file.
    """
    tasks_json = load_vscode_json(path)

    try:
        tasks = Tasks(**tasks_json)
    except pydantic.ValidationError as e:
        raise TasksFileInvalid(f"Tasks file not valid: {e}")

    # update global variables
    if tasks.default_build_task:
        RUNTIME_VARIABLES["${defaultBuildTask}"] = tasks.default_build_task.label

    for input_ in tasks.inputs:
        INPUTS[input_.id] = input_

    return tasks
