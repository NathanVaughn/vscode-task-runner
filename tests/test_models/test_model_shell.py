import pytest

from vscode_task_runner.models.enums import ShellTypeEnum
from vscode_task_runner.models.shell import (
    ShellConfiguration,
    ShellQuotingOptions,
    ShellQuotingOptionsEscape,
)


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


def test_shell_quoting_options_resolve_variables(
    default_build_task_patch: None,
) -> None:
    """
    Test resolving variables for ShellQuotingOptions
    """
    # Test with substitution
    s = ShellQuotingOptions(
        strong="${defaultBuildTask}",
        weak="${defaultBuildTask}",
        escape="${defaultBuildTask}",
    )
    s.resolve_variables()
    assert s.strong == "task1"
    assert s.weak == "task1"
    assert s.escape == "task1"


def test_shell_configuration_resolve_variables(default_build_task_patch: None) -> None:
    s = ShellConfiguration(
        executable="${defaultBuildTask}",
        args=["${defaultBuildTask}"],
        quoting=ShellQuotingOptions(
            strong="${defaultBuildTask}",
            weak="${defaultBuildTask}",
            escape=ShellQuotingOptionsEscape(
                escapeChar="${defaultBuildTask}", charsToEscape=["${defaultBuildTask}"]
            ),
        ),
    )

    s.resolve_variables()
    assert s.executable == "task1"
    assert s.args == ["task1"]
    assert isinstance(s.quoting, ShellQuotingOptions)
    assert s.quoting.strong == "task1"
    assert s.quoting.weak == "task1"
    assert isinstance(s.quoting.escape, ShellQuotingOptionsEscape)
    assert s.quoting.escape.escape_character == "task1"
    assert s.quoting.escape.characters_to_escape == ["task1"]
