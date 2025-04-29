import pytest

from vscode_task_runner.models.enums import ShellTypeEnum
from vscode_task_runner.models.shell import ShellConfiguration


@pytest.mark.parametrize(
    "shell_config, expected_shell_type",
    (
        (ShellConfiguration(executable="/bin/bash"), ShellTypeEnum.SH),
        (ShellConfiguration(executable="/bin/fish"), ShellTypeEnum.SH),
        (ShellConfiguration(executable="/bin/zsh"), ShellTypeEnum.SH),
        (ShellConfiguration(executable="/bin/pwsh"), ShellTypeEnum.PowerShell),
        (
            ShellConfiguration(executable=r"C:\Program Files\Git\bin\bash.exe"),
            ShellTypeEnum.SH,
        ),
        (ShellConfiguration(executable="pwsh.exe"), ShellTypeEnum.PowerShell),
        (ShellConfiguration(executable="powershell.exe"), ShellTypeEnum.PowerShell),
        (ShellConfiguration(executable="cmd.exe"), ShellTypeEnum.CMD),
        (ShellConfiguration(executable="wsl.exe"), ShellTypeEnum.WSL),
    ),
)
def test_type_detection(
    shutil_which_patch: None,
    shell_config: ShellConfiguration,
    expected_shell_type: ShellTypeEnum,
):
    """
    Test the type detection of the shell configuration.
    """
    assert shell_config.type_ == expected_shell_type
