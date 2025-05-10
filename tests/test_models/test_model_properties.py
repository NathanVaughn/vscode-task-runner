import pytest

from vscode_task_runner.models.enums import ShellQuotingEnum
from vscode_task_runner.models.options import CommandOptions
from vscode_task_runner.models.properties import (
    BaseCommandProperties,
    CommandProperties,
)
from vscode_task_runner.models.strings import QuotedStringConfig


@pytest.fixture
def command_properties() -> CommandProperties:
    return CommandProperties(
        windows=BaseCommandProperties(command="Windows"),
        linux=BaseCommandProperties(command="Linux"),
        osx=BaseCommandProperties(command="OSX"),
    )


def test_command_properties_os_linux(
    linux: None, command_properties: CommandProperties
) -> None:
    """
    Ensure correct command properties are returned for Linux.
    """
    assert command_properties.os is not None
    assert command_properties.os.command == "Linux"


def test_command_properties_os_windows(
    windows: None, command_properties: CommandProperties
) -> None:
    """
    Ensure correct command properties are returned for Windows.
    """
    assert command_properties.os is not None
    assert command_properties.os.command == "Windows"


def test_command_properties_os_osx(
    osx: None, command_properties: CommandProperties
) -> None:
    """
    Ensure correct command properties are returned for OSX.
    """
    assert command_properties.os is not None
    assert command_properties.os.command == "OSX"


def test_command_properties_resolve_variables(
    linux: None, default_build_task_mock: None
) -> None:
    """
    Ensure resolve variables works for command properties.
    """
    cp = CommandProperties(
        linux=BaseCommandProperties(command="${defaultBuildTask}"),
    )
    cp.resolve_variables()

    assert cp.os is not None
    assert cp.os.command == "task1"


def test_base_command_properties_resolve_variables(
    default_build_task_mock: None,
) -> None:
    """
    Ensure resolve variables works for base command properties.
    """
    cp = BaseCommandProperties(
        command=QuotedStringConfig(
            value="${defaultBuildTask}", quoting=ShellQuotingEnum.escape
        ),
        options=CommandOptions(),
        args=[
            QuotedStringConfig(
                value="${defaultBuildTask}", quoting=ShellQuotingEnum.escape
            ),
            "${defaultBuildTask}",
        ],
    )
    cp.resolve_variables()

    assert cp.command == QuotedStringConfig(
        value="task1", quoting=ShellQuotingEnum.escape
    )
    assert cp.args == [
        QuotedStringConfig(value="task1", quoting=ShellQuotingEnum.escape),
        "task1",
    ]
