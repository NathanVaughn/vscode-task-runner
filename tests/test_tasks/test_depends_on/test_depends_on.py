import pytest

from tests.conftest import load_task


@pytest.mark.parametrize(
    "task_label, expected",
    [("Test1", ["Test2"]), ("Test2", ["Test3", "Test4"]), ("Test3", [])],
)
def test_depends_on(linux: None, task_label: str, expected: list[str]) -> None:
    task = load_task(__file__, task_label)
    assert [d.label for d in task.depends_on] == expected
