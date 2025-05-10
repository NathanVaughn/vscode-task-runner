from tests.conftest import task_obj
from vscode_task_runner import executor


def test_is_virtual_task() -> None:
    t1 = task_obj(__file__, "test1")
    assert executor.is_virtual_task(t1) is False

    t2 = task_obj(__file__, "test2")
    assert executor.is_virtual_task(t2) is False

    t3 = task_obj(__file__, "test3")
    assert executor.is_virtual_task(t3) is True
