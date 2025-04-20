from enum import Enum
from typing import Dict, Optional, Union

from pydantic import BaseModel, ConfigDict, FilePath, RootModel

from vscode_task_runner2.constants import PLATFORM_KEY


class ShellQuoting(Enum):
    """
    Enum for shell quoting options
    """

    # https://github.com/microsoft/vscode/blob/eef30e7165e19b33daa1e15e92fa34ff4a5df0d3/src/vs/workbench/contrib/tasks/common/tasks.ts#L59-L60
    escape = 1
    strong = 2
    weak = 3


class ShellQuotingOptionsEscape(BaseModel):
    # https://github.com/microsoft/vscode/blob/eef30e7165e19b33daa1e15e92fa34ff4a5df0d3/src/vs/workbench/contrib/tasks/common/tasks.ts#L70-L71
    escapeChar: str
    charsToEscape: list[str]


class ShellQuotingOptions(BaseModel):
    """
    Shell quoting options
    """

    # https://github.com/microsoft/vscode/blob/eef30e7165e19b33daa1e15e92fa34ff4a5df0d3/src/vs/workbench/contrib/tasks/common/tasks.ts#L65-L83

    strong: Optional[str] = None
    """
    The character used for strong quoting.
    """
    escape: Optional[Union[ShellQuotingOptionsEscape, str]] = None
    """
    The character used to do character escaping.
    """
    weak: Optional[str] = None
    """
    The character used for weak quoting.
    """


class ShellConfiguration(BaseModel):
    """
    Shell configuration settings
    """

    # https://github.com/microsoft/vscode/blob/eef30e7165e19b33daa1e15e92fa34ff4a5df0d3/src/vs/workbench/contrib/tasks/common/tasks.ts#L85-L100

    executable: Optional[FilePath] = None
    """
    The shell executable.
    """
    args: Optional[list[str]] = None
    """
    The args to be passed to the shell executable.
    """
    quoting: Optional[ShellQuotingOptions] = None
    """
    Which kind of quotes the shell supports.
    """


class CommandOptions(BaseModel):
    """
    Regular options
    """

    # https://github.com/microsoft/vscode/blob/eef30e7165e19b33daa1e15e92fa34ff4a5df0d3/src/vs/workbench/contrib/tasks/common/tasks.ts#L102-L120

    shell: Optional[ShellConfiguration] = None
    """
    The shell to use if the task is a shell command.
    """
    cwd: Optional[str] = None
    """
    The current working directory of the executed program or shell.
    If omitted, the current working directory is used.
    Uses a string instead of DirectoryPath to allow for paths that may not exist
    on certain platforms.
    """
    env: Dict[str, str] = {}
    """
    The environment of the executed program or shell.
    If omitted, the current environment is used.
    """


class QuotedString(BaseModel):
    """
    Dataclass for complex arguments
    """

    # https://github.com/microsoft/vscode/blob/eef30e7165e19b33daa1e15e92fa34ff4a5df0d3/src/vs/workbench/contrib/tasks/common/tasks.ts#L315-L318

    value: Union[str, list[str]]
    quoting: ShellQuoting = ShellQuoting.strong


class QuotedStringType(RootModel):
    """
    Dataclass for most valid string types
    """

    root: Union[str, list[str], QuotedString]


class OSOption(BaseModel):
    """
    Dataclass for options that can be overriden for a specific OS
    """

    model_config = ConfigDict(extra="allow")

    args: Optional[QuotedStringType] = None
    command: Optional[QuotedStringType] = None
    options: Optional[CommandOptions] = None


class OSOptions(BaseModel):
    """
    Dataclass for a list of options based on the OS
    """

    windows: Optional[OSOption] = None
    linux: Optional[OSOption] = None
    osx: Optional[OSOption] = None

    @property
    def os(self) -> Union[OSOption, None]:
        """
        Get the OS option for the current OS
        """
        if PLATFORM_KEY == "windows":
            return self.windows
        elif PLATFORM_KEY == "linux":
            return self.linux
        elif PLATFORM_KEY == "osx":
            return self.osx
