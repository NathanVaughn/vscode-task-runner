import os

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
            QuotedStringConfig(value="${env:TEST1}", quoting=ShellQuotingEnum.escape),
            QuotedStringConfig(value="result1", quoting=ShellQuotingEnum.escape),
        ),
        (
            QuotedStringConfig(
                value=["${env:TEST1}", "${env:TEST2}"], quoting=ShellQuotingEnum.weak
            ),
            QuotedStringConfig(
                value=["result1", "result2"], quoting=ShellQuotingEnum.weak
            ),
        ),
    ),
)
def test_wsc_resolving(input_: QuotedStringConfig, output: str) -> None:
    # test resolving variables for a QuotedStringConfig

    # set temp variables to test
    os.environ["TEST1"] = "result1"
    os.environ["TEST2"] = "result2"

    # variables resolve in place
    input_.resolve_variables()

    # test equivalency
    assert input_ == output

    del os.environ["TEST1"]
    del os.environ["TEST2"]
