import pytest

from tests.conftest import task_obj


@pytest.mark.parametrize(
    "label, is_supported",
    [
        ("Task1", False),  # npm
        ("Task2", False),  # background task
        ("Task3", True),  # yes
    ],
)
def test_task_is_supported(label: str, is_supported: bool) -> None:
    """
    Test is_supported method.
    """
    task = task_obj(__file__, label)
    assert task.is_supported() is is_supported
