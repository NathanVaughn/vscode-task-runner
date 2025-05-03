from typing import List

import pytest

from vscode_task_runner.constants import DEFAULT_OS_QUOTING, DEFAULT_SHELL_QUOTING
from vscode_task_runner.models.enums import ShellQuotingEnum, ShellTypeEnum
from vscode_task_runner.models.shell import (
    ShellConfiguration,
    ShellQuotingOptions,
)
from vscode_task_runner.models.strings import CommandString, QuotedString
from vscode_task_runner.vscode import terminal_task_system


@pytest.mark.parametrize(
    "shell_config, shell_quoting",
    [
        (
            ShellConfiguration(executable="/bin/bash"),
            DEFAULT_SHELL_QUOTING[ShellTypeEnum.SH],
        ),
        (ShellConfiguration(executable="/bin/bash"), DEFAULT_OS_QUOTING["linux"]),
        (ShellConfiguration(executable="notreablah"), DEFAULT_OS_QUOTING["linux"]),
    ],
)
def test_get_quoting_options(
    linux: None,
    shutil_which_patch: None,
    shell_config: ShellConfiguration,
    shell_quoting: ShellConfiguration,
) -> None:
    assert terminal_task_system.get_quoting_options(shell_config) == shell_quoting


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
        terminal_task_system._add_all_argument(
            shell_command_args, configured_shell_args
        )
        == expected
    )


@pytest.mark.parametrize(
    "shell_config, command_line, expected",
    [
        (
            ShellConfiguration(executable="pwsh.exe", args=[]),
            "command1 command2",
            ["-Command", "command1 command2"],
        ),
        (
            ShellConfiguration(executable="pwsh.exe", args=["-Command"]),
            "command1 command2",
            ["-Command", "command1 command2"],
        ),
        (
            ShellConfiguration(executable="bash.exe", args=[]),
            "command1 command2",
            ["-c", "command1 command2"],
        ),
        (
            ShellConfiguration(executable="wsl.exe", args=[]),
            "command1 command2",
            ["-e", "command1 command2"],
        ),
        (
            ShellConfiguration(executable="cmd.exe", args=[]),
            "command1 command2",
            ["/d", "/c", "command1 command2"],
        ),
        (
            ShellConfiguration(executable="blah.exe", args=[]),
            "command1 command2",
            ["-c", "command1 command2"],
        ),
    ],
)
def test_create_shell_launch_config_windows(
    windows: None,
    shutil_which_patch: None,
    shell_config: ShellConfiguration,
    command_line: str,
    expected: List[str],
) -> None:
    assert (
        terminal_task_system.create_shell_launch_config(shell_config, command_line)
        == expected
    )


@pytest.mark.parametrize(
    "shell_config, command_line, expected",
    [
        (
            ShellConfiguration(executable="pwsh", args=[]),
            "command1 command2",
            ["-Command", "command1 command2"],
        ),
        (
            ShellConfiguration(executable="bash", args=[]),
            "command1 command2",
            ["-c", "command1 command2"],
        ),
    ],
)
def test_create_shell_launch_config_linux(
    linux: None,
    shutil_which_patch: None,
    shell_config: ShellConfiguration,
    command_line: str,
    expected: List[str],
) -> None:
    assert (
        terminal_task_system.create_shell_launch_config(shell_config, command_line)
        == expected
    )


@pytest.mark.parametrize(
    "shell_type, shell_quoting_options, task_command, args, expected",
    [
        (
            ShellTypeEnum.PowerShell,
            DEFAULT_SHELL_QUOTING[ShellTypeEnum.PowerShell],
            "command1",
            ["arg1", "arg2"],
            "command1 arg1 arg2",
        ),
        (
            ShellTypeEnum.PowerShell,
            DEFAULT_SHELL_QUOTING[ShellTypeEnum.PowerShell],
            "command1",
            ["arg1 arg2"],
            "command1 'arg1 arg2'",
        ),
        (
            ShellTypeEnum.PowerShell,
            DEFAULT_SHELL_QUOTING[ShellTypeEnum.PowerShell],
            "command1",
            [QuotedString(value="arg1 arg2", quoting=ShellQuotingEnum.strong)],
            "command1 'arg1 arg2'",
        ),
        (
            ShellTypeEnum.PowerShell,
            DEFAULT_SHELL_QUOTING[ShellTypeEnum.PowerShell],
            "command1",
            [QuotedString(value="arg1 arg2", quoting=ShellQuotingEnum.escape)],
            "command1 arg1` arg2",
        ),
        (
            ShellTypeEnum.PowerShell,
            DEFAULT_SHELL_QUOTING[ShellTypeEnum.PowerShell],
            "command1",
            [QuotedString(value="arg1 arg2", quoting=ShellQuotingEnum.weak)],
            'command1 "arg1 arg2"',
        ),
        (
            ShellTypeEnum.PowerShell,
            DEFAULT_SHELL_QUOTING[ShellTypeEnum.PowerShell],
            "command1",
            [],
            "command1",
        ),
        (
            ShellTypeEnum.PowerShell,
            DEFAULT_SHELL_QUOTING[ShellTypeEnum.PowerShell],
            "command one",
            ["arg"],
            "& 'command one' arg",
        ),
        (
            ShellTypeEnum.CMD,
            DEFAULT_SHELL_QUOTING[ShellTypeEnum.CMD],
            "command one",
            ["arg1 arg2"],
            '""command one" "arg1 arg2""',
        ),
        (
            ShellTypeEnum.PowerShell,
            DEFAULT_SHELL_QUOTING[ShellTypeEnum.PowerShell],
            "command1",
            ["'123'"],
            "command1 '123'",
        ),
        (
            ShellTypeEnum.PowerShell,
            DEFAULT_SHELL_QUOTING[ShellTypeEnum.PowerShell],
            "command1",
            [QuotedString(value='"arg1 arg2"', quoting=ShellQuotingEnum.weak)],
            'command1 ""arg1 arg2""',
        ),
        (
            ShellTypeEnum.CMD,
            DEFAULT_SHELL_QUOTING[ShellTypeEnum.CMD],
            "command one",
            [QuotedString(value='"arg1 arg2"', quoting=ShellQuotingEnum.escape)],
            '"command one" "arg1 arg2"',
        ),
        (
            ShellTypeEnum.CMD,
            ShellQuotingOptions(escape="\\"),
            "command one",
            [QuotedString(value='"arg1 arg2"', quoting=ShellQuotingEnum.escape)],
            'command one "arg1\\ arg2"',
        ),
    ],
)
def test_build_shell_command_line_windows(
    windows: None,
    shell_type: ShellTypeEnum,
    shell_quoting_options: ShellQuotingOptions,
    task_command: CommandString,
    args: List[CommandString],
    expected: str,
) -> None:
    assert (
        terminal_task_system.build_shell_command_line(
            shell_type, shell_quoting_options, task_command, args
        )
        == expected
    )


@pytest.mark.parametrize(
    "shell_type, shell_quoting_options, task_command, args, expected",
    [
        (
            ShellTypeEnum.PowerShell,
            DEFAULT_SHELL_QUOTING[ShellTypeEnum.PowerShell],
            "command one",
            ["arg"],
            "'command one' arg",
        ),
        (
            ShellTypeEnum.SH,
            DEFAULT_SHELL_QUOTING[ShellTypeEnum.SH],
            "command1",
            ["\\'hello world\\'"],
            "command1 \\'hello world\\'",
        ),
        (
            ShellTypeEnum.SH,
            ShellQuotingOptions(
                escape="\\",  # test with a single string escape
                strong="'",
                weak='"',
            ),
            "command1",
            ["\\'hello world\\'"],
            "command1 '\\'hello world\\''",
        ),
    ],
)
def test_build_shell_command_line_linux(
    linux: None,
    shell_type: ShellTypeEnum,
    shell_quoting_options: ShellQuotingOptions,
    task_command: CommandString,
    args: List[CommandString],
    expected: str,
) -> None:
    assert (
        terminal_task_system.build_shell_command_line(
            shell_type, shell_quoting_options, task_command, args
        )
        == expected
    )
