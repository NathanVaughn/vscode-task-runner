import os

import pyjson5

from vtr.exceptions import TasksFileNotFound


def load_vscode_tasks_data(path: str = os.getcwd()) -> dict:
    """
    Given a working directory, loads the vscode tasks config, and replaces
    all the variables. Returns raw dict data and the filename that was loaded.
    """
    tasks_json = os.path.join(path, ".vscode", "tasks.json")

    if not os.path.isfile(tasks_json):
        raise TasksFileNotFound(f"Tasks file not found at {tasks_json}")

    with open(tasks_json, "r") as fp:
        # work around `read` positional argument differences
        return pyjson5.decode(fp.read())
