from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional, Union


@dataclass
class ShellQuotingOptionsEscape:
    # https://github.com/microsoft/vscode/blob/eef30e7165e19b33daa1e15e92fa34ff4a5df0d3/src/vs/workbench/contrib/tasks/common/tasks.ts#L70-L71
    escape_character: str
    characters_to_escape: List[str]


@dataclass
class ShellQuotingOptions:
    # https://github.com/microsoft/vscode/blob/eef30e7165e19b33daa1e15e92fa34ff4a5df0d3/src/vs/workbench/contrib/tasks/common/tasks.ts#L65-L83
    strong: Optional[str] = None
    escape: Optional[Union[ShellQuotingOptionsEscape, str]] = None
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
    Unknown = auto()


@dataclass
class ShellConfiguration:
    executable: Optional[str] = None
    args: Optional[List[str]] = None
    quoting: Optional[ShellQuotingOptions] = None


@dataclass
class QuotedString:
    value: str
    quoting: ShellQuoting


CommandString = Union[str, QuotedString]
# https://github.com/microsoft/vscode/blob/eef30e7165e19b33daa1e15e92fa34ff4a5df0d3/src/vs/workbench/contrib/tasks/common/tasks.ts#L320
