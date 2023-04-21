import pytest

import src.task_parser


@pytest.mark.parametrize(
    "environment_variable",
    [("VSCODE_TASK_RUNNER_TEST", "abc123")],
    indirect=True,
)
def test_replace_env_vars(environment_variable: None) -> None:
    assert (
        src.task_parser.replace_env_vars("prefix ${env:VSCODE_TASK_RUNNER_TEST} suffix")
        == "prefix abc123 suffix"
    )
