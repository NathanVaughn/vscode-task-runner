import pytest

from tests.conftest import tasks_obj
from vscode_task_runner.exceptions import TasksFileNotFound


def test_parsing_missing() -> None:
    with pytest.raises(TasksFileNotFound):
        tasks_obj("notreal")
