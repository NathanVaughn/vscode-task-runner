import pytest

from tests.conftest import load_task


@pytest.mark.parametrize(
    "task_label, expected",
    [("Test1", "process"), ("Test2", "shell"), ("Test3", "process")],
)
def test_type_pass(task_label: str, expected: str) -> None:
    task = load_task(__file__, task_label)
    assert task.type_ == expected


def test_type_fail() -> None:
    task = load_task(__file__, "Test4")
    with pytest.raises(ValueError):
        assert task.type_ == "notanoption"
