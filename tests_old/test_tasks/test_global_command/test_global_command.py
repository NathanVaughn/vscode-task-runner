# https://github.com/NathanVaughn/vscode-task-runner/issues/87

from typing import List

import pytest

from tests_old.conftest import load_task


@pytest.mark.parametrize(
    "task_label, expected",
    [
        ("Test1", ["ls"]),
        ("Test2", ["cd"]),
        ("Test3", ["ls", "-la"]),
        ("Test4", ["cd", ".."]),
    ],
)
def test_global_command_structure(
    task_label: str, expected: List[str], shutil_which_patch: None
) -> None:
    task = load_task(__file__, task_label)
    assert task.subprocess_command() == expected
    assert task.is_virtual is False
