import os
import pathlib

import pydantic
import pyjson5

from vscode_task_runner.constants import CODE_WORKSPACE_SUFFIX, TASKS_FILE
from vscode_task_runner.exceptions import TasksFileInvalid, TasksFileNotFound
from vscode_task_runner.models.tasks import Tasks
from vscode_task_runner.variables.runtime import INPUTS, RUNTIME_VARIABLES


def load_vscode_json(path: str) -> dict:
    """
    Given a working directory, loads the vscode tasks config.
    """
    # some values that will be set later
    file_to_use = None
    tasks_key = False

    # possible paths
    tasks_json = os.path.join(path, TASKS_FILE)
    code_workspace_json = os.path.join(path, CODE_WORKSPACE_SUFFIX)
    code_workspace_jsons = sorted(pathlib.Path(path).glob(f"*{CODE_WORKSPACE_SUFFIX}"))

    # prefer the tasks.json file
    if os.path.isfile(tasks_json):
        file_to_use = tasks_json

    # fallback to the code workspace file if it exists
    elif os.path.isfile(code_workspace_json):
        file_to_use = code_workspace_json
        tasks_key = True

    # last resort, open first file that ends with .code-workspace
    else:
        for file in code_workspace_jsons:
            if file.is_file():
                file_to_use = file
                tasks_key = True
                break

    # if we didn't find any file, raise an error
    if not file_to_use:
        raise TasksFileNotFound(f"No suitable tasks file found in {path}")

    with open(file_to_use, "r", encoding="utf-8") as fp:
        # use pyjson 5 to deal with comments and other bad syntax
        data = pyjson5.decode(fp.read())

    if tasks_key:
        # if we are using a code workspace file, we need to get the tasks key
        if "tasks" not in data:
            raise TasksFileInvalid("Tasks key not found in code workspace file")
        data = data["tasks"]

    return data


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
