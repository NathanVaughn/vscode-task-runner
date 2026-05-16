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
        ["--help"],
        ["-h"],
        ["-h", "Test1"],
        ["-h", "Test1", "--extra1"],
    ),
)
def test_show_help(sys_argv: list[str]) -> None:
    """
    Test that the help is shown and the program exits when -h or --help is passed
    """
    with pytest.raises(SystemExit):
        console.parse_args(sys_argv, ["Test1", "Test2", "Test3"])


@pytest.mark.parametrize(
    "sys_argv",
    (
        ["--complete"],
        ["--complete", "Test1"],
        ["--complete", "Test1", "--extra1"],
    ),
)
def test_show_complete(sys_argv: list[str]) -> None:
    """
    Test that the complete message is shown and the program exits when --complete is passed
    """
    with pytest.raises(SystemExit):
        console.parse_args(sys_argv, ["Test1", "Test2", "Test3"])


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
        ["--invalid-option", "Test1"],  # invalid option
        ["Test1", "InvalidTask"],  # invalid task label
        ["--input=Key1", "Test1"],  # invalid input format
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

    env = {
        "VTR_SKIP_SUMMARY": "1",
        "VTR_CONTINUE_ON_ERROR": "1",
        "VTR_INPUT_Key1": "Value1=2",  # test equals sign in value
        "VTR_DEFAULT_BUILD_TASK": "Test1",
    }

    # Clear environment variables for the test
    for var in env:
        if var in os.environ:
            del os.environ[var]

    console.parse_args(
        [
            "--skip-summary",
            "--continue-on-error",
            "--input=Key1=Value1=2",
            "--default-build-task=Test1",
            "Test1",
        ],
        ["Test1"],
    )

    for var, val in env.items():
        assert os.environ[var] == val

        # Wipe environment variables after the test
        del os.environ[var]
