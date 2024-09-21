from typing import Any

import pytest

from tests.conftest import load_task
from vscode_task_runner.exceptions import InvalidValue
from vscode_task_runner.models import QuotedString, ShellQuoting


@pytest.mark.parametrize(
    "task_label, expected",
    [
        ("Test1", []),
        ("Test2", []),
        ("Test3", [QuotedString(value="te st", quoting=ShellQuoting.Escape)]),
        ("Test4", ["te", "st"]),
        (
            "Test5",
            [
                QuotedString(value="te st", quoting=ShellQuoting.Escape),
                QuotedString(value="$te st2", quoting=ShellQuoting.Weak),
                "test3",
            ],
        ),
    ],
)
def test_args_pass(task_label: str, expected: Any) -> None:
    task = load_task(__file__, task_label)
    assert task.args == expected


def test_args_fail() -> None:
    task = load_task(__file__, "Test6")
    with pytest.raises(InvalidValue):
        assert task.args == {"key": "value"}
