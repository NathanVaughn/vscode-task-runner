import os
import platform
from typing import Dict, Literal

from vscode_task_runner2.models.enums import ShellTypeEnum, TaskTypeEnum
from vscode_task_runner2.models.shell import (
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

PLATFORM_KEY = PLATFORM_KEYS[platform.system()]  # type: ignore


OPTIONS_KEY = "options"

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

DEFAULT_OS_QUOTING: Dict[_VSC_PLATFORM_LITERAL, ShellQuotingOptions] = {
    "linux": DEFAULT_SHELL_QUOTING[ShellTypeEnum.SH],
    "osx": DEFAULT_SHELL_QUOTING[ShellTypeEnum.SH],
    "windows": DEFAULT_SHELL_QUOTING[ShellTypeEnum.PowerShell],
}

DEFAULT_TASK_TYPE = TaskTypeEnum.process
