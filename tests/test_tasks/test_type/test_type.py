import pytest

from tests.conftest import load_task
from vscode_task_runner.exceptions import UnsupportedValue
from vscode_task_runner.models import TaskType


@pytest.mark.parametrize(
    "task_label, expected",
    [
        ("Test1", TaskType.process),
        ("Test2", TaskType.shell),
        ("Test3", TaskType.process),
    ],
)
def test_type_pass(task_label: str, expected: str) -> None:
    task = load_task(__file__, task_label)
    assert task.type_ == expected


def test_type_fail() -> None:
    task = load_task(__file__, "Test4")
    with pytest.raises(UnsupportedValue):
        assert task.type_ == "notanoption"
