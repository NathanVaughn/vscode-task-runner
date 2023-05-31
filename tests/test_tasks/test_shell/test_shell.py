from typing import Tuple

import pytest

from tests.conftest import load_task
from vtr.models import ShellConfiguration, ShellType


@pytest.mark.parametrize(
    "task_label, expected",
    [("Test1", (ShellConfiguration(executable="/bin/bash"), ShellType.SH))],
)
def test_shell(
    task_label: str,
    expected: Tuple[ShellConfiguration, ShellType],
    shutil_which_patch: None,
) -> None:
    # patch shutil.which to return whatever gets put in for this test
    task = load_task(__file__, task_label)
    assert task.shell == expected


@pytest.mark.parametrize(
    "task_label",
    [("Test2")],
)
def test_shell_empty(
    task_label: str,
    shutil_which_patch: None,
) -> None:
    # patch shutil.which to return whatever gets put in for this test
    task = load_task(__file__, task_label)
    assert task.shell[0].executable is not None
