from typing import List

import pytest

from tests.conftest import load_task


@pytest.mark.parametrize(
    "task_label, expected",
    [("Test1", ["/bin/bash", "-c", '"echo.sh"']), ("Test2", ["python", "echo.py"])],
)
def test_subprocess_command(
    task_label: str, expected: List[str], shutil_which_patch: None
) -> None:
    task = load_task(__file__, task_label)
    assert task.subprocess_command() == expected


@pytest.mark.parametrize(
    "task_label, expected",
    [
        ("Test1", ["/bin/bash", "-c", '"echo.sh extra args"']),
        ("Test2", ["python", "echo.py", "extra", "args"]),
        ("Test4", ["/bin/bash", "-c", "echo 'Hello World!' extra args"]),
        ("Test5", ["/bin/bash", "-c", "echo.sh extra args"]),
    ],
)
def test_subprocess_command_extra_args(
    task_label: str, expected: List[str], shutil_which_patch: None
) -> None:
    task = load_task(__file__, task_label)
    assert task.subprocess_command(extra_args=["extra", "args"]) == expected
