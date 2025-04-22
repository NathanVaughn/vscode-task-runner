from enum import Enum, auto


class InputTypeEnum(str, Enum):
    """
    Enum for input types.
    """

    promptString = "promptString"
    pickString = "pickString"
    command = "command"


class ShellTypeEnum(Enum):
    """
    Enum for different shell types
    """

    SH = auto()
    PowerShell = auto()
    CMD = auto()
    WSL = auto()
    Unknown = auto()


class ShellQuotingEnum(Enum):
    """
    Enum for shell quoting options
    """

    # https://github.com/microsoft/vscode/blob/eef30e7165e19b33daa1e15e92fa34ff4a5df0d3/src/vs/workbench/contrib/tasks/common/tasks.ts#L59-L60
    escape = "escape"
    strong = "strong"
    weak = "weak"


class DependsOrderEnum(str, Enum):
    """
    Enum for task execution order
    """

    parallel = "parallel"
    sequence = "sequence"


class TaskTypeEnum(str, Enum):
    """
    Enum for task types
    """

    process = "process"
    shell = "shell"


class GroupKindEnum(str, Enum):
    """
    Enum for task groups
    """

    build = "build"
    test = "test"
    none = "none"
