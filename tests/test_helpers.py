from typing import Any, Type

import pytest
from pytest_mock import MockerFixture

import vtr.helpers
from vtr.models import CommandString, QuotedString, ShellQuoting, ShellType


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
    shell_executable: str, shell_type: ShellType, mocker: MockerFixture
) -> None:
    # patch shutil.which to return whatever gets put in for this test
    mocker.patch("shutil.which", new=lambda x: x)

    assert vtr.helpers.identify_shell_type(shell_executable) == shell_type


def test_identify_shell_type_fail() -> None:
    # test for when the given shell path does not resolve to anything
    with pytest.raises(FileNotFoundError):
        vtr.helpers.identify_shell_type("/not/real")


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
    assert vtr.helpers.stringify(input_) == output


@pytest.mark.parametrize(
    "input_, exception",
    (
        ({}, ValueError),
        (None, ValueError),
        ({"key": "value"}, ValueError),
    ),
)
def test_stringify_fail(input_: Any, exception: Type[Exception]) -> None:
    # test the stringify helper exceptions
    with pytest.raises(exception):
        vtr.helpers.stringify(input_)


@pytest.mark.parametrize(
    "input_, output",
    (("test", "test"), (["te", "st"], "te st")),
)
def test_combine_string(input_: Any, output: str) -> None:
    assert vtr.helpers.combine_string(input_) == output


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
    assert vtr.helpers.load_command_string(input_) == output


@pytest.mark.parametrize(
    "input_, exception",
    (
        ({}, KeyError),
        (None, ValueError),
        ({"key": "value"}, KeyError),
    ),
)
def test_load_command_string_fail(input_: Any, exception: Type[Exception]) -> None:
    with pytest.raises(exception):
        vtr.helpers.load_command_string(input_)
