import os

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


def test_parse_args_env_vars() -> None:
    """
    Test the argument parser with options that turn into environment variables
    """

    # Clear environment variables for the test
    if "VTR_SKIP_SUMMARY" in os.environ:
        del os.environ["VTR_SKIP_SUMMARY"]
    if "VTR_CONTINUE_ON_ERROR" in os.environ:
        del os.environ["VTR_CONTINUE_ON_ERROR"]

    console.parse_args(["Test1", "--skip-summary", "--continue-on-error"], ["Test1"])

    assert os.environ["VTR_SKIP_SUMMARY"] == "1"
    assert os.environ["VTR_CONTINUE_ON_ERROR"] == "1"

    # Wipe environment variables after the test
    del os.environ["VTR_SKIP_SUMMARY"]
    del os.environ["VTR_CONTINUE_ON_ERROR"]
