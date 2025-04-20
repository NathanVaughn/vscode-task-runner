from enum import Enum
from typing import Dict, Optional, Union

from pydantic import BaseModel, ConfigDict, FilePath, RootModel, field_validator

from vscode_task_runner2.constants import PLATFORM_KEY


class ShellQuoting(Enum):
    """
    Enum for shell quoting options
    """

    # https://github.com/microsoft/vscode/blob/eef30e7165e19b33daa1e15e92fa34ff4a5df0d3/src/vs/workbench/contrib/tasks/common/tasks.ts#L59-L60
    escape = "escape"
    strong = "strong"
    weak = "weak"


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

    @field_validator("env", mode="before")
    def stringify_env(cls, value: Dict[str, str]) -> Dict[str, str]:
        """
        Convert all values in the env dictionary to strings.
        Vscode tends to be pretty lax about only allowing strings,
        so replicate that behavior. `null` is not allowed.
        """
        response = {}
        for k, v in value.items():
            if v is None:
                raise ValueError(f"Environment variable {k} cannot be null")

            # convert booleans to strings in the same way as JS
            response[k] = str(v).lower() if isinstance(v, bool) else str(v)

        return response


class QuotedString(BaseModel):
    """
    Dataclass for complex arguments
    """

    # https://github.com/microsoft/vscode/blob/eef30e7165e19b33daa1e15e92fa34ff4a5df0d3/src/vs/workbench/contrib/tasks/common/tasks.ts#L315-L318

    value: Union[str, list[str]]
    quoting: ShellQuoting


CommandString = Union[QuotedString, str]
# https://github.com/microsoft/vscode/blob/eef30e7165e19b33daa1e15e92fa34ff4a5df0d3/src/vs/workbench/contrib/tasks/common/tasks.ts#L320


class StringListStringQuotedStringType(RootModel):
    root: Union[QuotedString, list[str], str]
    # ! Order is important for pydantic

    def export_command_string(self) -> CommandString:
        """
        Export the string data to a CommandString
        """
        if isinstance(self.root, str):
            return self.root
        elif isinstance(self.root, list):
            return " ".join(self.root)
        elif isinstance(self.root, QuotedString):
            return self.root
        else:
            raise ValueError(f"Invalid type {type(self.root)}")


class TaskConfig(BaseModel):
    """
    Dataclass for task config options
    """

    model_config = ConfigDict(extra="allow")

    args: Optional[list[CommandString]] = None
    """
    Arguments passed to the command. This allows a list of strings or a list of quoted strings
    """
    command: Optional[StringListStringQuotedStringType] = None
    """
    Command that the task will run. This allows a single string, list of strings, or a quoted string
    """
    options: Optional[CommandOptions] = None
    """
    Options for this task.
    """


class OSConfigs(BaseModel):
    """
    Dataclass for a list of configs based on the OS
    """

    windows: Optional[TaskConfig] = None
    linux: Optional[TaskConfig] = None
    osx: Optional[TaskConfig] = None

    @property
    def os(self) -> Union[TaskConfig, None]:
        """
        Get the OS option for the current OS
        """
        if PLATFORM_KEY == "windows":
            return self.windows
        elif PLATFORM_KEY == "linux":
            return self.linux
        elif PLATFORM_KEY == "osx":
            return self.osx
