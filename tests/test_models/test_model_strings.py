# import os

import pytest

from vscode_task_runner.models.enums import ShellQuotingEnum
from vscode_task_runner.models.strings import (
    CommandString,
    CommandStringConfig,
    QuotedString,
    QuotedStringConfig,
    cs_value,
    csc_value,
)


@pytest.mark.parametrize(
    "input_, output",
    (
        ("test", "test"),
        (["test1", "test2"], "test1 test2"),
        (QuotedStringConfig(value="test", quoting=ShellQuotingEnum.escape), "test"),
        (
            QuotedStringConfig(value=["test1", "test2"], quoting=ShellQuotingEnum.weak),
            "test1 test2",
        ),
    ),
)
def test_csc_value(input_: CommandStringConfig, output: str) -> None:
    # test converting a CommandStringConfig to a value
    assert csc_value(input_) == output


@pytest.mark.parametrize(
    "input_, output",
    (
        ("test", "test"),
        (QuotedString(value="test", quoting=ShellQuotingEnum.escape), "test"),
    ),
)
def test_cs_value(input_: CommandString, output: str) -> None:
    # test converting a CommandString to a value
    assert cs_value(input_) == output


@pytest.mark.parametrize(
    "input_, output",
    (
        (
            QuotedStringConfig(
                value="${defaultBuildTask}", quoting=ShellQuotingEnum.escape
            ),
            QuotedStringConfig(value="task1", quoting=ShellQuotingEnum.escape),
        ),
        (
            QuotedStringConfig(
                value=["${defaultBuildTask}"], quoting=ShellQuotingEnum.weak
            ),
            QuotedStringConfig(value=["task1"], quoting=ShellQuotingEnum.weak),
        ),
    ),
)
def test_quoted_string_config_resolve_variables(
    default_build_task_mock: None,
    input_: QuotedStringConfig,
    output: QuotedStringConfig,
) -> None:
    """
    Test resolving variables for a QuotedStringConfig
    """
    # variables resolve in place
    input_.resolve_variables()
    assert input_ == output
