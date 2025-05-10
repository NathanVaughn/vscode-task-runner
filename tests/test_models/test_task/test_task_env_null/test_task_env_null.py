import pytest

from tests.conftest import tasks_obj
from vscode_task_runner.exceptions import TasksFileInvalid


def test_parsing() -> None:
    """
    Test that an exception is raised when the env block contains a null value
    """
    with pytest.raises(TasksFileInvalid):
        tasks_obj(__file__)
