import pytest
from pytest_mock import MockerFixture

import vscode_task_runner.variables
from vscode_task_runner.exceptions import UnsupportedValue, UnsupportedVariable


@pytest.mark.parametrize(
    "environment_variable",
    [("VTR_INPUT_test", "abc123")],
    indirect=True,
)
def test_get_input_value_env(environment_variable: None) -> None:
    """
    Ensure the input value is correctly obtained from the environment.
    """
    assert (
        vscode_task_runner.variables.get_input_value("test", [{"id": "test"}])
        == "abc123"
    )


def test_get_input_value_text(mocker: MockerFixture) -> None:
    """
    Ensure a text input value is correctly obtained from the user.
    """
    mocker.patch.object(vscode_task_runner.variables.questionary, attribute="text")

    vscode_task_runner.variables.get_input_value(
        "test", [{"id": "test", "description": "desc", "type": "promptString"}]
    )
    vscode_task_runner.variables.questionary.text.assert_called_once_with(
        "desc", default=""
    )


def test_get_input_value_password(mocker: MockerFixture) -> None:
    """
    Ensure a password input value is correctly obtained from the user.
    """
    mocker.patch.object(vscode_task_runner.variables.questionary, attribute="password")

    vscode_task_runner.variables.get_input_value(
        "test",
        [
            {
                "id": "test",
                "description": "desc",
                "type": "promptString",
                "password": True,
            }
        ],
    )
    vscode_task_runner.variables.questionary.password.assert_called_once_with(
        "desc", default=""
    )


def test_get_input_value_select(mocker: MockerFixture) -> None:
    """
    Ensure a select input value is correctly obtained from the user.
    """
    mocker.patch.object(vscode_task_runner.variables.questionary, attribute="select")

    vscode_task_runner.variables.get_input_value(
        "test",
        [
            {
                "id": "test",
                "description": "desc",
                "type": "pickString",
                "options": ["option1", "option2"],
            }
        ],
    )
    vscode_task_runner.variables.questionary.select.assert_called_once_with(
        "desc", choices=["option1", "option2"], default=None
    )


def test_get_input_value_unsupported() -> None:
    """
    Ensure an exception is raised if an unsupported input type is encountered.
    """
    with pytest.raises(UnsupportedValue):
        vscode_task_runner.variables.get_input_value(
            "test", [{"id": "test", "type": "command"}]
        )


def test_get_input_variables_values(mocker: MockerFixture) -> None:
    """
    Ensure the input variables are correctly identified.
    """
    mocker.patch.object(
        vscode_task_runner.variables, attribute="get_input_value", return_value=None
    )

    commands = [
        [
            "command1",
            "command2 ${input:var1}",
            "command3 ${input:var2}",
            "command4 ${input:var2}",
            "command5 ${{input:var3}}",
        ]
    ]

    vscode_task_runner.variables.get_input_variables_values(commands)

    # ensure only two calls were made
    # set does not maintain order
    vscode_task_runner.variables.get_input_value.assert_has_calls(
        [mocker.call("var1", []), mocker.call("var2", [])], any_order=True
    )


@pytest.mark.parametrize(
    "environment_variable",
    [("VSCODE_TASK_RUNNER_TEST", "abc123")],
    indirect=True,
)
def test_replace_env_variables(environment_variable: None) -> None:
    """
    Ensure environment variables are replaced correctly.
    """
    assert (
        vscode_task_runner.variables.replace_env_variables(
            "prefix ${env:VSCODE_TASK_RUNNER_TEST} suffix"
        )
        == "prefix abc123 suffix"
    )


@pytest.mark.parametrize(
    "environment_variable",
    [("VSCODE_TASK_RUNNER_TEST", "abc123")],
    indirect=True,
)
def test_replace_static_variables(environment_variable: None) -> None:
    # From VS Code docs:
    # https://code.visualstudio.com/docs/editor/tasks#_variable-substitution
    # Note: Not all properties will accept variable substitution.
    # Specifically, only command, args, and options support variable substitution.

    input_data = {
        "key1": "${relativeFileDirname}",  # make sure this does not cause error
        "options": {
            "command": "${env:VSCODE_TASK_RUNNER_TEST}",
            "key4": ["string1", 123, "${env:VSCODE_TASK_RUNNER_TEST}"],
        },
        "key5": False,
        "key6": [{"options": "${env:VSCODE_TASK_RUNNER_TEST}"}],
    }

    output_data = {
        "key1": "${relativeFileDirname}",
        "options": {"command": "abc123", "key4": ["string1", 123, "abc123"]},
        "key5": False,
        "key6": [{"options": "abc123"}],
    }

    assert (
        vscode_task_runner.variables.replace_static_variables(input_data) == output_data
    )


def test_replace_static_variables_unsupported() -> None:
    """
    Ensure an exception is raised if an unsupported variable is encountered.
    """
    with pytest.raises(UnsupportedVariable):
        vscode_task_runner.variables.replace_static_variables(
            {"options": "${lineNumber}"}
        )


def test_replace_runtime_variables() -> None:
    """
    Ensure runtime variables are replaced correctly.
    """

    input_data = ["prefix ${input:test} suffix", "prefix ${defaultBuildTask} suffix"]

    output_data = ["prefix test_input suffix", "prefix Task1 suffix"]

    assert (
        vscode_task_runner.variables.replace_runtime_variables(
            input_data, {"test": "test_input"}, "Task1"
        )
        == output_data
    )
