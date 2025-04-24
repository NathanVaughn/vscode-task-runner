import pytest

from tests.conftest import tasks_obj
from vscode_task_runner.exceptions import TasksFileInvalid


def test_default_input() -> None:
    # testing where default not provided in list of options
    with pytest.raises(TasksFileInvalid):
        tasks_obj(__file__)
