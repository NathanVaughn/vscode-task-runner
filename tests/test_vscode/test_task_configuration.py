from typing import Optional

import pytest

from vscode_task_runner.models.enums import ShellQuotingEnum
from vscode_task_runner.models.strings import (
    CommandString,
    CommandStringConfig,
    QuotedString,
    QuotedStringConfig,
)
from vscode_task_runner.vscode.task_configuration import shell_string


@pytest.mark.parametrize(
    "input_, output",
    (
        (None, None),
        ("Test", "Test"),
        (["Test1", "Test2"], "Test1 Test2"),
        (
            QuotedStringConfig(value="Test", quoting=ShellQuotingEnum.weak),
            QuotedString(value="Test", quoting=ShellQuotingEnum.weak),
        ),
        (
            QuotedStringConfig(value=["Test1", "Test2"], quoting=ShellQuotingEnum.weak),
            QuotedString(value="Test1 Test2", quoting=ShellQuotingEnum.weak),
        ),
    ),
)
def test_shell_string(
    input_: Optional[CommandStringConfig], output: Optional[CommandString]
) -> None:
    assert shell_string(input_) == output
