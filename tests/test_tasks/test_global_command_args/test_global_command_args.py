from typing import List

import pytest

from tests.conftest import load_task


# when global args are added to a global command, things get weird
# Args are only applied for tasks with matching commands and any additional
# args defined in the task are appended
@pytest.mark.parametrize(
    "task_label, expected",
    [
        ("Test1", ["ls", "-la"]),
        ("Test2", ["cd"]),
        ("Test3", ["ls", "-la", "-lb"]),
        ("Test4", ["cd", ".."]),
    ],
)
def test_global_command_args(
    task_label: str, expected: List[str], shutil_which_patch: None
) -> None:
    task = load_task(__file__, task_label)
    assert task.subprocess_command() == expected
    assert task.is_virtual is False
