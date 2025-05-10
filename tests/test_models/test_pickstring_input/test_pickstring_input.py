import pytest

from tests.conftest import tasks_obj
from vscode_task_runner.exceptions import TasksFileInvalid


def test_pickstring_input() -> None:
    # testing where pick string does not have an option set
    with pytest.raises(TasksFileInvalid):
        tasks_obj(__file__)
