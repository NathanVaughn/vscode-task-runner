import pytest

from tests.conftest import task_obj


def test_full(linux: None) -> None:
    task = task_obj(__file__, "env-test")

    assert task._new_env() == {"TEST3": "value3", "TEST4": "value4"}


def test_partial1(linux: None) -> None:
    task = task_obj(__file__, "env-test")
    task.options = None

    assert task._new_env() == {"TEST4": "value4"}


def test_partial2(linux: None) -> None:
    task = task_obj(__file__, "env-test")
    task.linux = None

    assert task._new_env() == {"TEST3": "value3"}


def test_partial3(linux: None) -> None:
    task = task_obj(__file__, "env-test")
    task.linux = None
    task._tasks.options = None

    assert task._new_env() == {"TEST3": "value3"}


def test_partial4(linux: None) -> None:
    task = task_obj(__file__, "env-test")
    task._tasks.options = None

    assert task._new_env() == {"TEST3": "value3", "TEST4": "value4"}


def test_partial5(linux: None) -> None:
    task = task_obj(__file__, "env-test")
    task.options = None
    task.linux = None

    assert task._new_env() == {"TEST1": "value1", "TEST2": "value2"}


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
    env = task.env_use()
    assert env["TEST3"] == "value3"
    # moer than just test3 and 4
    assert len(env) >= 2
