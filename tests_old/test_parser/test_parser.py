import os

import pytest

import vscode_task_runner_old.parser
from vscode_task_runner_old.exceptions import TasksFileNotFound


def test_load_vscode_tasks_data_comments() -> None:
    # make sure file with comments can be loaded successfully
    assert (
        vscode_task_runner_old.parser.load_vscode_tasks_data(
            path=os.path.dirname(__file__)
        )["version"]
        == "2.0.0"
    )


def test_load_vscode_tasks_data_notfound() -> None:
    with pytest.raises(TasksFileNotFound):
        vscode_task_runner_old.parser.load_vscode_tasks_data(path="/not/real/")
