import os
import platform
from typing import Dict

from vscode_task_runner.models.enums import PlatformEnum, ShellTypeEnum
from vscode_task_runner.models.shell import (
    ShellQuotingOptions,
    ShellQuotingOptionsEscape,
)

# Current OS
CURRENT_PLATFORM = PlatformEnum(platform.system())

# VS Code constants
TASKS_FILE = os.path.join(".vscode", "tasks.json")
CODE_WORKSPACE_SUFFIX = ".code-workspace"

# https://github.com/microsoft/vscode/blob/ab7c32a5b5275c3fa9552675b6b6035888068fd7/src/vs/workbench/contrib/tasks/browser/terminalTaskSystem.ts#L163-L191
DEFAULT_SHELL_QUOTING = {
    ShellTypeEnum.CMD: ShellQuotingOptions(strong='"'),
    ShellTypeEnum.PowerShell: ShellQuotingOptions(
        escape=ShellQuotingOptionsEscape(
            escapeChar="`", charsToEscape=[" ", '"', "'", "(", ")"]
        ),
        strong="'",
        weak='"',
    ),
    # zsh is the exact same as bash, so combine the 2
    ShellTypeEnum.SH: ShellQuotingOptions(
        escape=ShellQuotingOptionsEscape(
            escapeChar="\\", charsToEscape=[" ", '"', "'"]
        ),
        strong="'",
        weak='"',
    ),
}
"""
Shell quoting settings that are used for each shell type.
"""

DEFAULT_OS_QUOTING: Dict[PlatformEnum, ShellQuotingOptions] = {
    PlatformEnum.linux: DEFAULT_SHELL_QUOTING[ShellTypeEnum.SH],
    PlatformEnum.osx: DEFAULT_SHELL_QUOTING[ShellTypeEnum.SH],
    PlatformEnum.windows: DEFAULT_SHELL_QUOTING[ShellTypeEnum.PowerShell],
}
"""
Shell quoting settings that are used by default for each OS.
"""
