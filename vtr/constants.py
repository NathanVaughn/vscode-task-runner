import os
import platform
from typing import Dict, Literal

from vtr.models import ShellQuotingOptions, ShellQuotingOptionsEscape, ShellType

PLATFORM_KEYS: Dict[
    Literal["Windows", "Linux", "Darwin"], Literal["windows", "linux", "osx"]
] = {
    "Windows": "windows",
    "Linux": "linux",
    "Darwin": "osx",
}

PLATFORM_KEY = PLATFORM_KEYS[platform.system()]  # type: ignore

PREDEFINED_VARIABLES = {
    "${userHome}": os.path.expanduser("~"),
    "${workspaceFolder}": os.getcwd(),
    "${workspaceFolderBasename}": os.path.basename(os.getcwd()),
    "${pathSeparator}": os.path.sep,
    "${cwd}": os.getcwd(),
}

OPTIONS_KEY = "options"

# https://github.com/microsoft/vscode/blob/ab7c32a5b5275c3fa9552675b6b6035888068fd7/src/vs/workbench/contrib/tasks/browser/terminalTaskSystem.ts#L163-L191
DEFAULT_SHELL_QUOTING = {
    ShellType.CMD: ShellQuotingOptions(strong='"'),
    ShellType.PowerShell: ShellQuotingOptions(
        escape=ShellQuotingOptionsEscape(
            escape_character="`", characters_to_escape=[" ", '"', "'", "(", ")"]
        ),
        strong="'",
        weak='"',
    ),
    # zsh is the exact same as bash, so combine the 2
    ShellType.SH: ShellQuotingOptions(
        escape=ShellQuotingOptionsEscape(
            escape_character="\\", characters_to_escape=[" ", '"', "'"]
        ),
        strong="'",
        weak='"',
    ),
}

DEFAULT_OS_QUOTING = {
    "linux": DEFAULT_SHELL_QUOTING[ShellType.SH],
    "osx": DEFAULT_SHELL_QUOTING[ShellType.SH],
    "windows": DEFAULT_SHELL_QUOTING[ShellType.PowerShell],
}
