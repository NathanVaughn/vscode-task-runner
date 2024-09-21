from typing import Any, Type

import pytest

import vscode_task_runner.helpers
from vscode_task_runner.exceptions import FileNotFound, InvalidValue
from vscode_task_runner.models import (
    CommandString,
    QuotedString,
    ShellQuoting,
    ShellType,
)


@pytest.mark.parametrize(
    "shell_executable, shell_type",
    (
        ("pwsh.exe", ShellType.PowerShell),
        (
            "C:\\Program Files\\WindowsApps\\Microsoft.PowerShell_7.3.4.0_x64__8wekyb3d8bbwe\\pwsh.exe",
            ShellType.PowerShell,
        ),
        ("powershell.exe", ShellType.PowerShell),
        (
            "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe",
            ShellType.PowerShell,
        ),
        ("/opt/microsoft/powershell/7/pwsh", ShellType.PowerShell),
        ("C:\\Program Files\\Git\\bin\\bash.exe", ShellType.SH),
        ("bash.exe", ShellType.SH),
        ("wsl.exe", ShellType.WSL),
        ("C:\\Windows\\System32\\wsl.exe", ShellType.WSL),
        (
            "C:\\Program Files\\WindowsApps\\MicrosoftCorporationII.WindowsSubsystemForLinux_1.2.5.0_x64__8wekyb3d8bbwe\\wsl.exe",
            ShellType.WSL,
        ),
        ("cmd.exe", ShellType.CMD),
        ("/bin/sh", ShellType.SH),
        ("/bin/bash", ShellType.SH),
        ("/usr/bin/bash", ShellType.SH),
        ("/bin/zsh", ShellType.SH),
        ("/bin/fish", ShellType.SH),
        ("notreal", ShellType.Unknown),
        ("python.exe", ShellType.Unknown),
    ),
)
def test_identify_shell_type(
    shell_executable: str, shell_type: ShellType, shutil_which_patch: None
) -> None:
    # patch shutil.which to return whatever gets put in for this test
    assert (
        vscode_task_runner.helpers.identify_shell_type(shell_executable) == shell_type
    )


def test_identify_shell_type_fail() -> None:
    # test for when the given shell path does not resolve to anything
    with pytest.raises(FileNotFound):
        vscode_task_runner.helpers.identify_shell_type("/not/real")


@pytest.mark.parametrize(
    "input_, output",
    (
        ("test", "test"),
        (1, "1"),
        (2.0, "2.0"),
        (True, "True"),
    ),
)
def test_stringify_pass(input_: Any, output: str) -> None:
    # test the stringify helper
    assert vscode_task_runner.helpers.stringify(input_) == output


@pytest.mark.parametrize(
    "input_, exception",
    (
        ({}, InvalidValue),
        (None, InvalidValue),
        ({"key": "value"}, InvalidValue),
    ),
)
def test_stringify_fail(input_: Any, exception: Type[Exception]) -> None:
    # test the stringify helper exceptions
    with pytest.raises(exception):
        vscode_task_runner.helpers.stringify(input_)


@pytest.mark.parametrize(
    "input_, output",
    (("test", "test"), (["te", "st"], "te st")),
)
def test_combine_string(input_: Any, output: str) -> None:
    assert vscode_task_runner.helpers.combine_string(input_) == output


@pytest.mark.parametrize(
    "input_, output",
    (
        ("test", "test"),
        (["test"], "test"),
        (["te", "st"], "te st"),
        (
            {"value": "test", "quoting": "escape"},
            QuotedString(value="test", quoting=ShellQuoting.Escape),
        ),
        (
            {"value": ["test"], "quoting": "escape"},
            QuotedString(value="test", quoting=ShellQuoting.Escape),
        ),
        (
            {"value": ["te", "st"], "quoting": "escape"},
            QuotedString(value="te st", quoting=ShellQuoting.Escape),
        ),
    ),
)
def test_load_command_string_pass(input_: Any, output: CommandString) -> None:
    assert vscode_task_runner.helpers.load_command_string(input_) == output


@pytest.mark.parametrize(
    "input_, exception",
    (
        ({}, KeyError),
        (None, InvalidValue),
        ({"key": "value"}, KeyError),
    ),
)
def test_load_command_string_fail(input_: Any, exception: Type[Exception]) -> None:
    with pytest.raises(exception):
        vscode_task_runner.helpers.load_command_string(input_)
