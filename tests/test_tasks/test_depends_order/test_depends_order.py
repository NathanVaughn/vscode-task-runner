import pytest

from tests.conftest import load_task


@pytest.mark.parametrize(
    "task_label, expected",
    [
        ("TestParallel", "parallel"),
        ("TestSequence", "sequence"),
        ("TestDefault", "sequence"),
    ],
)
def test_depends_order(task_label: str, expected: str) -> None:
    """
    Test that depends_order property correctly identifies the dependsOrder setting.
    """
    task = load_task(__file__, task_label)
    assert task.depends_order == expected
