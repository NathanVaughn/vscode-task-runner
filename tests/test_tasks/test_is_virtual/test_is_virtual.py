import pytest

from tests.conftest import load_task


@pytest.mark.parametrize(
    "task_label, expected",
    [("Test1", True), ("Test2", False), ("Test3", True), ("Test4", False)],
)
def test_is_virtual(linux: None, task_label: str, expected: bool) -> None:
    task = load_task(__file__, task_label)
    assert task.is_virtual is expected
