import pytest

from tests.conftest import task_obj
from vscode_task_runner import executor


def test_full(linux: None) -> None:
    task = task_obj(__file__, "env-test")

    assert executor._new_task_env(task) == {"TEST3": "value3", "TEST4": "value4"}


def test_partial1(linux: None) -> None:
    task = task_obj(__file__, "env-test")
    task.options = None

    assert executor._new_task_env(task) == {"TEST4": "value4"}


def test_partial2(linux: None) -> None:
    task = task_obj(__file__, "env-test")
    task.linux = None

    assert executor._new_task_env(task) == {"TEST3": "value3"}


def test_partial3(linux: None) -> None:
    task = task_obj(__file__, "env-test")
    task.linux = None
    task._tasks.options = None

    assert executor._new_task_env(task) == {"TEST3": "value3"}


def test_partial4(linux: None) -> None:
    task = task_obj(__file__, "env-test")
    task._tasks.options = None

    assert executor._new_task_env(task) == {"TEST3": "value3", "TEST4": "value4"}


def test_partial5(linux: None) -> None:
    task = task_obj(__file__, "env-test")
    task.options = None
    task.linux = None

    assert executor._new_task_env(task) == {"TEST1": "value1", "TEST2": "value2"}


@pytest.mark.parametrize(
    "environment_variable",
    [("TEST3", "oldvalue")],
    indirect=True,
)
def test_task_env(environment_variable: None) -> None:
    """
    Test that the task environment is merged with the current environment.
    """
    task = task_obj(__file__, "env-test")
    env = executor.task_env(task)
    assert env["TEST3"] == "value3"
    # moer than just test3 and 4
    assert len(env) >= 2
