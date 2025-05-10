import os
import platform
from typing import Dict, Literal

from vscode_task_runner.models.enums import ShellTypeEnum
from vscode_task_runner.models.shell import (
    ShellQuotingOptions,
    ShellQuotingOptionsEscape,
)

TASKS_FILE = os.path.join(".vscode", "tasks.json")


_PY_PLATFORM_LITERAL = Literal["Windows", "Linux", "Darwin"]
_VSC_PLATFORM_LITERAL = Literal["windows", "linux", "osx"]

PLATFORM_KEYS: Dict[_PY_PLATFORM_LITERAL, _VSC_PLATFORM_LITERAL] = {
    "Windows": "windows",
    "Linux": "linux",
    "Darwin": "osx",
}
"""
Conversion of Python platform.system() to VS Code platform key.
"""

PLATFORM_KEY = PLATFORM_KEYS[platform.system()]  # type: ignore
"""
Current VS Code platform key
"""

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

DEFAULT_OS_QUOTING: Dict[_VSC_PLATFORM_LITERAL, ShellQuotingOptions] = {
    "linux": DEFAULT_SHELL_QUOTING[ShellTypeEnum.SH],
    "osx": DEFAULT_SHELL_QUOTING[ShellTypeEnum.SH],
    "windows": DEFAULT_SHELL_QUOTING[ShellTypeEnum.PowerShell],
}
"""
Shell quoting settings that are used by default for each OS.
"""
