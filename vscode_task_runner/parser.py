import os

import pydantic
import pyjson5

from vscode_task_runner.constants import TASKS_FILE
from vscode_task_runner.exceptions import TasksFileInvalid, TasksFileNotFound
from vscode_task_runner.models.tasks import Tasks
from vscode_task_runner.variables.runtime import INPUTS, RUNTIME_VARIABLES


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


def load_tasks(path: str = "") -> Tasks:
    """
    Load the model from the tasks.json file.
    """
    if not path:
        # this makes things easier for testing
        path = os.getcwd()

    tasks_json = load_vscode_json(path)

    try:
        tasks = Tasks(**tasks_json)
    except pydantic.ValidationError as e:
        raise TasksFileInvalid(f"Tasks file not valid: {e}")

    # update global variables
    if default_build_task := tasks.default_build_task():
        RUNTIME_VARIABLES["${defaultBuildTask}"] = default_build_task.label

    for input_ in tasks.inputs:
        INPUTS[input_.id] = input_

    return tasks
