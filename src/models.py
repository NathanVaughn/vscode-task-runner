from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional


@dataclass
class ShellQuotingOptionsEscape:
    # https://github.com/microsoft/vscode/blob/eef30e7165e19b33daa1e15e92fa34ff4a5df0d3/src/vs/workbench/contrib/tasks/common/tasks.ts#L70-L71
    escape_character: str
    characters_to_escape: list[str]


@dataclass
class ShellQuotingOptions:
    # https://github.com/microsoft/vscode/blob/eef30e7165e19b33daa1e15e92fa34ff4a5df0d3/src/vs/workbench/contrib/tasks/common/tasks.ts#L65-L83
    strong: Optional[str] = None
    escape: Optional[ShellQuotingOptionsEscape | str] = None
    weak: Optional[str] = None


class ShellQuoting(Enum):
    """
    Enum for shell quoting options
    """

    # https://github.com/microsoft/vscode/blob/eef30e7165e19b33daa1e15e92fa34ff4a5df0d3/src/vs/workbench/contrib/tasks/common/tasks.ts#L59-L60
    Strong = "strong"
    Weak = "weak"
    Escape = "escape"


class ShellType(Enum):
    SH = auto()
    PowerShell = auto()
    CMD = auto()
    WSL = auto()


@dataclass
class Shell:
    executable: str
    type_: ShellType


@dataclass
class ShellConfiguration:
    executable: Optional[str] = None
    args: Optional[list[str]] = None
    quoting: Optional[ShellQuotingOptions] = None


@dataclass
class QuotedString:
    value: str
    quoting: ShellQuoting
