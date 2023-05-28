from typing import Any

import pytest

from tests.conftest import load_task
from vtr.models import QuotedString, ShellQuoting


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
def test_args_pass(linux: None, task_label: str, expected: Any) -> None:
    task = load_task(__file__, task_label)
    assert task.args == expected


def test_args_fail(linux: None) -> None:
    task = load_task(__file__, "Test6")
    with pytest.raises(ValueError):
        assert task.args == {"key": "value"}
