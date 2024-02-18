import os

import pytest

import vtr.parser
from vtr.exceptions import TasksFileNotFound


def test_load_vscode_tasks_data_comments() -> None:
    # make sure file with comments can be loaded successfully
    assert (
        vtr.parser.load_vscode_tasks_data(path=os.path.dirname(__file__))["version"]
        == "2.0.0"
    )


def test_load_vscode_tasks_data_notfound() -> None:
    with pytest.raises(TasksFileNotFound):
        vtr.parser.load_vscode_tasks_data(path="/not/real/")
