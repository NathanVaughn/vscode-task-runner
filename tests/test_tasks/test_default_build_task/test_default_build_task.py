import pytest

from tests.conftest import load_task


@pytest.mark.parametrize(
    "task_label, expected",
    [("Test1", False), ("Test2", True), ("Test3", False), ("Test4", False)],
)
def test_is_default_build_task(task_label: str, expected: bool) -> None:
    task = load_task(__file__, task_label)
    assert task.is_default_build_task == expected
