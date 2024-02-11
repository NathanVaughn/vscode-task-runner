import pytest

import vtr.variables
from vtr.exceptions import UnsupportedVariable


@pytest.mark.parametrize(
    "environment_variable",
    [("VSCODE_TASK_RUNNER_TEST", "abc123")],
    indirect=True,
)
def test_replace_env_variables(environment_variable: None) -> None:
    assert (
        vtr.variables.replace_env_variables(
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

    assert vtr.variables.replace_static_variables(input_data) == output_data


def test_replace_static_variables_unsupported() -> None:
    with pytest.raises(UnsupportedVariable):
        vtr.variables.replace_static_variables({"options": "${lineNumber}"})
