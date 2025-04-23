import pytest

from tests.conftest import tasks_obj
from vscode_task_runner.exceptions import TasksFileInvalid


def test_parsing() -> None:
    with pytest.raises(TasksFileInvalid):
        tasks_obj(__file__)
