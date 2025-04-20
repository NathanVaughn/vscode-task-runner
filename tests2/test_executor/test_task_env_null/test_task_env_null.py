import pytest

from tests2.conftest import tasks_obj
from vscode_task_runner2.exceptions import TasksFileInvalid


def test_parsing() -> None:
    with pytest.raises(TasksFileInvalid):
        tasks_obj(__file__)
