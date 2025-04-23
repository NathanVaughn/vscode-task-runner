from typing import List

import pytest

import vscode_task_runner_old.console


@pytest.mark.parametrize(
    "in_args, out_labels, out_extra_args",
    [
        (["build"], ["build"], []),
        (["build", "test"], ["build", "test"], []),
        (["build", "--extra"], ["build"], ["--extra"]),
        (["build", "--extra1", "--extra2"], ["build"], ["--extra1", "--extra2"]),
        (["build", "--"], ["build"], []),
        (["build", "--", "--extra"], ["build"], ["--extra"]),
        (["build", "--extra1", "--", "extra2"], ["build"], ["--extra1", "extra2"]),
        (["test", "--", "--", "--reporter=json"], ["test"], ["--", "--reporter=json"]),
    ],
)
def test_parse_args_pass(
    in_args: List[str], out_labels: List[str], out_extra_args: List[str]
) -> None:
    task_choices = ["build", "test"]
    help_text = ""
    parse_result = vscode_task_runner_old.console.parse_args(
        in_args, task_choices, help_text
    )
    assert parse_result.task_labels == out_labels
    assert parse_result.extra_args == out_extra_args


def test_parse_args_error() -> None:
    task_choices = ["build", "test"]
    help_text = ""
    with pytest.raises(SystemExit):
        vscode_task_runner_old.console.parse_args(
            ["build", "test", "--extra"], task_choices, help_text
        )
