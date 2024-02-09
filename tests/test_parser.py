import pytest

import vtr.parser


@pytest.mark.parametrize(
    "environment_variable",
    [("VSCODE_TASK_RUNNER_TEST", "abc123")],
    indirect=True,
)
def test_replace_env_vars(environment_variable: None) -> None:
    assert (
        vtr.parser.replace_env_vars("prefix ${env:VSCODE_TASK_RUNNER_TEST} suffix")
        == "prefix abc123 suffix"
    )


@pytest.mark.parametrize(
    "environment_variable",
    [("VSCODE_TASK_RUNNER_TEST", "abc123")],
    indirect=True,
)
def test_replace_variables_data(environment_variable: None) -> None:
    input_data = {
        "key1": "${env:VSCODE_TASK_RUNNER_TEST}",
        "key2": {
            "key3": "${env:VSCODE_TASK_RUNNER_TEST}",
            "key4": ["string1", 123, "${env:VSCODE_TASK_RUNNER_TEST}"],
        },
        "key5": False,
    }

    output_data = {
        "key1": "abc123",
        "key2": {"key3": "abc123", "key4": ["string1", 123, "abc123"]},
        "key5": False,
    }

    assert vtr.parser.replace_variables_data(input_data) == output_data
