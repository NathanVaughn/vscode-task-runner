from typing import Any

import pytest
import questionary
from pytest_mock import MockerFixture

from tests.conftest import task_obj
from vscode_task_runner.utils.picker import determine_default_build_task


@pytest.mark.parametrize(
    "environment_variable",
    [("VTR_DEFAULT_BUILD_TASK", "Task1")],
    indirect=True,
)
def test_env(environment_variable: None) -> None:
    """
    Test providing an environment variable to the function.
    """
    task1 = task_obj(__file__, "Task1")
    task2 = task_obj(__file__, "Task2")
    task3 = task_obj(__file__, "Task3")

    tasks = [task1, task2, task3]
    task = determine_default_build_task(tasks)
    assert task is not None
    assert task.label == "Task1"


def test_pick(mocker: MockerFixture) -> None:
    """
    Test picking an option.
    """

    class mock_select:
        def __init__(self, *args: Any, **kwds: Any) -> None: ...

        def ask(self):
            return "Task1"

    mocker.patch.object(questionary, "select", new=mock_select)

    task1 = task_obj(__file__, "Task1")
    task2 = task_obj(__file__, "Task2")
    task3 = task_obj(__file__, "Task3")

    tasks = [task1, task2, task3]
    task = determine_default_build_task(tasks)

    assert task is not None
    assert task.label == "Task1"
