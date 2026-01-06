"""Integration tests for CLI input flags."""

import os

import pytest

from vscode_task_runner.console import set_input_environment_variables


def test_set_input_environment_variables() -> None:
    """
    Test setting VTR_INPUT_* environment variables from CLI input values
    """
    # Clear any existing test input env vars
    for key in list(os.environ.keys()):
        if key.startswith("VTR_INPUT_test"):
            del os.environ[key]

    # Set input values
    input_values = {"test_foo": "bar", "test_env": "production"}
    set_input_environment_variables(input_values)

    # Verify environment variables were set
    assert os.environ["VTR_INPUT_test_foo"] == "bar"
    assert os.environ["VTR_INPUT_test_env"] == "production"

    # Clean up
    del os.environ["VTR_INPUT_test_foo"]
    del os.environ["VTR_INPUT_test_env"]


def test_set_input_environment_variables_precedence() -> None:
    """
    Test that CLI input values override existing environment variables
    """
    # Set an initial environment variable
    os.environ["VTR_INPUT_test_override"] = "original_value"

    # Override with CLI input
    input_values = {"test_override": "cli_value"}
    set_input_environment_variables(input_values)

    # Verify CLI value took precedence
    assert os.environ["VTR_INPUT_test_override"] == "cli_value"

    # Clean up
    del os.environ["VTR_INPUT_test_override"]


def test_set_input_environment_variables_empty_dict() -> None:
    """
    Test that setting empty input values works correctly
    """
    # Should not raise any errors
    set_input_environment_variables({})


def test_set_input_environment_variables_special_chars() -> None:
    """
    Test input IDs with special characters (hyphens, underscores)
    """
    input_values = {
        "test-hyphen": "value1",
        "test_underscore": "value2",
        "test-mixed_chars": "value3",
    }
    set_input_environment_variables(input_values)

    assert os.environ["VTR_INPUT_test-hyphen"] == "value1"
    assert os.environ["VTR_INPUT_test_underscore"] == "value2"
    assert os.environ["VTR_INPUT_test-mixed_chars"] == "value3"

    # Clean up
    del os.environ["VTR_INPUT_test-hyphen"]
    del os.environ["VTR_INPUT_test_underscore"]
    del os.environ["VTR_INPUT_test-mixed_chars"]


def test_set_input_environment_variables_empty_value() -> None:
    """
    Test that empty string values are set correctly
    """
    input_values = {"test_empty": ""}
    set_input_environment_variables(input_values)

    assert os.environ["VTR_INPUT_test_empty"] == ""

    # Clean up
    del os.environ["VTR_INPUT_test_empty"]
