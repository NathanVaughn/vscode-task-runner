from typing import Any

import pytest

from tests_old.conftest import load_task
from vscode_task_runner_old.models import QuotedString, ShellQuoting


@pytest.mark.parametrize(
    "task_label, expected",
    [
        ("Test1", "test"),
        ("Test2", "te st"),
        ("Test3", QuotedString(value="te st", quoting=ShellQuoting.Escape)),
        ("Test4", QuotedString(value="te st", quoting=ShellQuoting.Escape)),
    ],
)
def test_command(task_label: str, expected: Any) -> None:
    task = load_task(__file__, task_label)
    assert task.command == expected
