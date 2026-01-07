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


@pytest.mark.parametrize(
    "sys_argv, expected_input_values",
    (
        # Single input
        (
            ["Test1", "--input-foo=bar"],
            {"foo": "bar"},
        ),
        # Multiple inputs
        (
            ["Test1", "--input-env=prod", "--input-region=us-west"],
            {"env": "prod", "region": "us-west"},
        ),
        # Input with equals in value
        (
            ["Test1", "--input-key=value=with=equals"],
            {"key": "value=with=equals"},
        ),
        # Input with special chars in ID
        (
            ["Test1", "--input-my-input_v2=value"],
            {"my-input_v2": "value"},
        ),
        # Input with empty value
        (
            ["Test1", "--input-foo="],
            {"foo": ""},
        ),
        # Duplicate input flags (last wins)
        (
            ["Test1", "--input-env=dev", "--input-env=prod"],
            {"env": "prod"},
        ),
    ),
)
def test_parse_args_with_inputs(
    sys_argv: list[str], expected_input_values: dict[str, str]
) -> None:
    """
    Test parsing --input-<id>=<value> flags
    """
    result = console.parse_args(sys_argv, ["Test1", "Test2", "Test3"])
    assert result.input_values == expected_input_values


def test_parse_args_inputs_combined_with_other_flags() -> None:
    """
    Test --input-* combined with --skip-summary and --continue-on-error
    """
    # Clear environment variables for the test
    if "VTR_SKIP_SUMMARY" in os.environ:
        del os.environ["VTR_SKIP_SUMMARY"]
    if "VTR_CONTINUE_ON_ERROR" in os.environ:
        del os.environ["VTR_CONTINUE_ON_ERROR"]

    result = console.parse_args(
        ["Test1", "--skip-summary", "--input-env=prod", "--continue-on-error"],
        ["Test1"],
    )

    assert result.task_labels == ["Test1"]
    assert result.input_values == {"env": "prod"}
    assert result.extra_args == []
    assert os.environ.get("VTR_SKIP_SUMMARY") == "1"
    assert os.environ.get("VTR_CONTINUE_ON_ERROR") == "1"

    # Wipe environment variables after the test
    del os.environ["VTR_SKIP_SUMMARY"]
    del os.environ["VTR_CONTINUE_ON_ERROR"]


def test_parse_args_inputs_with_extra_args() -> None:
    """
    Test --input-* combined with -- extra args
    """
    result = console.parse_args(
        ["Test1", "--input-env=prod", "--", "-v", "--output=file.txt"],
        ["Test1"],
    )

    assert result.task_labels == ["Test1"]
    assert result.input_values == {"env": "prod"}
    assert result.extra_args == ["-v", "--output=file.txt"]


def test_parse_args_input_without_value() -> None:
    """
    Test error when --input-id is missing =value
    """
    with pytest.raises(SystemExit):
        console.parse_args(["Test1", "--input-foo"], ["Test1"])
