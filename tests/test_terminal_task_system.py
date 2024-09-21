from typing import List, Union

import pytest

import vscode_task_runner.terminal_task_system
from vscode_task_runner.constants import DEFAULT_OS_QUOTING, DEFAULT_SHELL_QUOTING
from vscode_task_runner.models import (
    CommandString,
    QuotedString,
    ShellConfiguration,
    ShellQuoting,
    ShellQuotingOptions,
    ShellType,
)


@pytest.mark.parametrize(
    "shell_type, shell_config_input, shell_config_output",
    [
        (
            ShellType.SH,
            ShellConfiguration(quoting=ShellQuotingOptions(strong="abc", weak="def")),
            ShellConfiguration(quoting=ShellQuotingOptions(strong="abc", weak="def")),
        ),
        (
            ShellType.SH,
            ShellConfiguration(),
            ShellConfiguration(quoting=DEFAULT_SHELL_QUOTING[ShellType.SH]),
        ),
        (
            ShellType.Unknown,
            ShellConfiguration(),
            ShellConfiguration(quoting=DEFAULT_OS_QUOTING["linux"]),
        ),
    ],
)
def test_get_quoting_options(
    linux: None,
    shell_type: ShellType,
    shell_config_input: ShellConfiguration,
    shell_config_output: ShellConfiguration,
) -> None:
    vscode_task_runner.terminal_task_system.get_quoting_options(
        shell_type, shell_config_input
    )
    assert shell_config_input == shell_config_output


@pytest.mark.parametrize(
    "shell_command_args, configured_shell_args, expected",
    [
        (
            ["/a", "-b", "--c"],
            ["command1", "arg1"],
            ["command1", "arg1", "/a", "-b", "--c"],
        ),
        (
            ["/a", "-b", "--c"],
            ["/b", "-c", "--d"],
            ["/b", "-c", "--d", "/a", "-b", "--c"],
        ),
        (
            ["/a", "-b", "--c"],
            ["/a", "-b", "--c"],
            ["/a", "-b", "--c"],
        ),
    ],
)
def test__add_all_argument(
    shell_command_args: List[str], configured_shell_args: List[str], expected: List[str]
) -> None:
    assert (
        vscode_task_runner.terminal_task_system._add_all_argument(
            shell_command_args, configured_shell_args
        )
        == expected
    )


@pytest.mark.parametrize(
    "shell_type, shell_args, command_line, expected",
    [
        (
            ShellType.PowerShell,
            [],
            "command1 command2",
            ["-Command", "command1 command2"],
        ),
        (
            ShellType.PowerShell,
            ["-Command"],
            "command1 command2",
            ["-Command", "command1 command2"],
        ),
        (
            ShellType.PowerShell,
            "-Command",
            "command1 command2",
            ["-Command", "command1 command2"],
        ),
        (
            ShellType.SH,
            [],
            "command1 command2",
            ["-c", "command1 command2"],
        ),
        (
            ShellType.WSL,
            [],
            "command1 command2",
            ["-e", "command1 command2"],
        ),
        (
            ShellType.CMD,
            [],
            "command1 command2",
            ["/d", "/c", "command1 command2"],
        ),
        (
            ShellType.Unknown,
            [],
            "command1 command2",
            ["-c", "command1 command2"],
        ),
    ],
)
def test_create_shell_launch_config_windows(
    windows: None,
    shell_type: ShellType,
    shell_args: Union[List[str], str],
    command_line: str,
    expected: List[str],
) -> None:
    assert (
        vscode_task_runner.terminal_task_system.create_shell_launch_config(
            shell_type, shell_args, command_line
        )
        == expected
    )


@pytest.mark.parametrize(
    "shell_type, shell_args, command_line, expected",
    [
        (
            ShellType.PowerShell,
            [],
            "command1 command2",
            ["-Command", "command1 command2"],
        ),
        (
            ShellType.SH,
            [],
            "command1 command2",
            ["-c", "command1 command2"],
        ),
    ],
)
def test_create_shell_launch_config_linux(
    linux: None,
    shell_type: ShellType,
    shell_args: Union[List[str], str],
    command_line: str,
    expected: List[str],
) -> None:
    assert (
        vscode_task_runner.terminal_task_system.create_shell_launch_config(
            shell_type, shell_args, command_line
        )
        == expected
    )


@pytest.mark.parametrize(
    "shell_type, shell_quoting_options, task_command, args, expected",
    [
        (
            ShellType.PowerShell,
            DEFAULT_SHELL_QUOTING[ShellType.PowerShell],
            "command1",
            ["arg1", "arg2"],
            "command1 arg1 arg2",
        ),
        (
            ShellType.PowerShell,
            DEFAULT_SHELL_QUOTING[ShellType.PowerShell],
            "command1",
            ["arg1 arg2"],
            "command1 'arg1 arg2'",
        ),
        (
            ShellType.PowerShell,
            DEFAULT_SHELL_QUOTING[ShellType.PowerShell],
            "command1",
            [QuotedString(value="arg1 arg2", quoting=ShellQuoting.Strong)],
            "command1 'arg1 arg2'",
        ),
        (
            ShellType.PowerShell,
            DEFAULT_SHELL_QUOTING[ShellType.PowerShell],
            "command1",
            [QuotedString(value="arg1 arg2", quoting=ShellQuoting.Escape)],
            "command1 arg1` arg2",
        ),
        (
            ShellType.PowerShell,
            DEFAULT_SHELL_QUOTING[ShellType.PowerShell],
            "command1",
            [QuotedString(value="arg1 arg2", quoting=ShellQuoting.Weak)],
            'command1 "arg1 arg2"',
        ),
        (
            ShellType.PowerShell,
            DEFAULT_SHELL_QUOTING[ShellType.PowerShell],
            "command1",
            [],
            "command1",
        ),
        (
            ShellType.PowerShell,
            DEFAULT_SHELL_QUOTING[ShellType.PowerShell],
            "command one",
            ["arg"],
            "& 'command one' arg",
        ),
        (
            ShellType.CMD,
            DEFAULT_SHELL_QUOTING[ShellType.CMD],
            "command one",
            ["arg1 arg2"],
            '""command one" "arg1 arg2""',
        ),
        (
            ShellType.PowerShell,
            DEFAULT_SHELL_QUOTING[ShellType.PowerShell],
            "command1",
            ["'123'"],
            "command1 '123'",
        ),
        (
            ShellType.PowerShell,
            DEFAULT_SHELL_QUOTING[ShellType.PowerShell],
            "command1",
            [QuotedString(value='"arg1 arg2"', quoting=ShellQuoting.Weak)],
            'command1 ""arg1 arg2""',
        ),
        (
            ShellType.CMD,
            DEFAULT_SHELL_QUOTING[ShellType.CMD],
            "command one",
            [QuotedString(value='"arg1 arg2"', quoting=ShellQuoting.Escape)],
            '"command one" "arg1 arg2"',
        ),
        (
            ShellType.CMD,
            ShellQuotingOptions(escape="\\"),
            "command one",
            [QuotedString(value='"arg1 arg2"', quoting=ShellQuoting.Escape)],
            'command one "arg1\\ arg2"',
        ),
    ],
)
def test_build_shell_command_line_windows(
    windows: None,
    shell_type: ShellType,
    shell_quoting_options: ShellQuotingOptions,
    task_command: CommandString,
    args: List[CommandString],
    expected: str,
) -> None:
    assert (
        vscode_task_runner.terminal_task_system.build_shell_command_line(
            shell_type, shell_quoting_options, task_command, args
        )
        == expected
    )
