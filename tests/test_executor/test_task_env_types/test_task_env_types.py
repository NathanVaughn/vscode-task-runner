from tests.conftest import task_obj
from vscode_task_runner import executor


def test_parsing() -> None:
    task = task_obj(__file__, "env-test")

    assert executor._new_task_env(task) == {
        "TEST1": "12.34",
        "TEST2": "56",
        "TEST3": "true",
        "TEST4": "value4",
    }
