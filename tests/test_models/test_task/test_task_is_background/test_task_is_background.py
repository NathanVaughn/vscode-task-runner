import pytest

from tests.conftest import task_obj


@pytest.mark.parametrize(
    "label, is_background",
    [
        ("Task1", True),  # explicitly yes, no command
        ("Task2", False),  # explicitly no, no command
        ("Task3", True),  # explicitly yes, with command
        ("Task4", False),  # explicitly no, with command
        ("Task5", True),  # not explicit, no command
        ("Task6", False),  # not explicit, with command, this is how vscode treats it
        ("Task7", False),  # not explicit, with different command
    ],
)
def test_is_background(label: str, is_background: bool) -> None:
    """
    Test is_background method.
    """
    task = task_obj(__file__, label)
    assert task.is_background_use() is is_background
