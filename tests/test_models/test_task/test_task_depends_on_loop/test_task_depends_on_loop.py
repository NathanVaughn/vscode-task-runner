import pytest

from tests.conftest import task_obj
from vscode_task_runner.exceptions import TasksFileInvalid


def test_self_referencing() -> None:
    """
    Test duplicate labels in the tasks.json file
    """
    with pytest.raises(TasksFileInvalid):
        task_obj(__file__, "Task3")
