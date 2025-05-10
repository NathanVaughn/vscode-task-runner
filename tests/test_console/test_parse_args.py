import pytest

from vscode_task_runner import console
from vscode_task_runner.models.arg_parser import ArgParseResult


@pytest.mark.parametrize(
    "sys_argv, expected",
    (
        (
            ["Test1", "Test2", "Test3"],
            ArgParseResult(task_labels=["Test1", "Test2", "Test3"], extra_args=[]),
        ),
        (
            ["Test1", "--", "extra1", "extra2"],
            ArgParseResult(task_labels=["Test1"], extra_args=["extra1", "extra2"]),
        ),
        (
            ["Test1", "--extra1", "--extra2"],
            ArgParseResult(task_labels=["Test1"], extra_args=["--extra1", "--extra2"]),
        ),
    ),
)
def test_parse_args(sys_argv: list[str], expected: ArgParseResult) -> None:
    """
    Test the argument parser
    """
    assert console.parse_args(sys_argv, ["Test1", "Test2", "Test3"]) == expected


@pytest.mark.parametrize(
    "sys_argv",
    (
        [],  # empty list
        ["--", "extra1", "extra2"],  # no task labels
        [
            "Test1",
            "Test2",
            "--extra1",
            "--extra2",
        ],  # extra args with more than one task
        [
            "Test1",
            "Test2",
            "--",
            "extra1",
            "extra2",
        ],  # extra args with more than one task
    ),
)
def test_parse_args_error(sys_argv: list[str]) -> None:
    """
    Test the argument parser
    """
    with pytest.raises(SystemExit):
        console.parse_args(sys_argv, ["Test1", "Test2", "Test3"])
