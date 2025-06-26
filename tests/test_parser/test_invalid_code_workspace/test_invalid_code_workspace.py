import pytest

from tests.conftest import tasks_obj
from vscode_task_runner.exceptions import TasksFileInvalid


def test_invalid_code_workspace() -> None:
    # ensure an error is raised when parsing invalid code workspace
    with pytest.raises(TasksFileInvalid):
        tasks_obj(__file__)
