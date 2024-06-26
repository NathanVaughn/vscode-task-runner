from typing import List

import pytest

import vtr.console


@pytest.mark.parametrize(
    "in_args, out_args, out_extra_args",
    [
        (["build"], ["build"], []),
        (["build", "test"], ["build", "test"], []),
        (["build", "--extra"], ["build"], ["--extra"]),
        (["build", "--extra1", "--extra2"], ["build"], ["--extra1", "--extra2"]),
    ],
)
def test_parse_args_pass(
    in_args: List[str], out_args: List[str], out_extra_args: List[str]
) -> None:
    task_choices = ["build", "test"]
    help_text = ""
    args, extra_args = vtr.console.parse_args(in_args, task_choices, help_text)
    assert args == out_args
    assert extra_args == out_extra_args


def test_parse_args_error() -> None:
    task_choices = ["build", "test"]
    help_text = ""
    with pytest.raises(SystemExit):
        vtr.console.parse_args(["build", "test", "--extra"], task_choices, help_text)
