from typing import Dict, Optional, Union

from pydantic import BaseModel, Field, field_validator

from vscode_task_runner2.constants import PLATFORM_KEY
from vscode_task_runner2.models.shell import ShellConfiguration
from vscode_task_runner2.models.strings import (
    CommandStringConfig,
)


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
    If omitted, the parent process' environment is used.
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


class BaseCommandProperties(BaseModel):
    """
    Dataclass for task config options
    """

    # https://github.com/microsoft/vscode/blob/e0c332665ce059efebb4477a90dd62e3aadcd688/src/vs/workbench/contrib/tasks/common/taskConfiguration.ts#L245-L263

    command: Optional[CommandStringConfig] = None
    """
    Command that the task will run. This allows a single string, list of strings, or a quoted string
    """
    options: Optional[CommandOptions] = None
    """
    Options for this task.
    """
    args: list[CommandStringConfig] = Field(default_factory=list)
    """
    Arguments passed to the command. This allows a list of strings or a list of quoted strings
    """
    # https://github.com/microsoft/vscode/blob/52592e3ca8f6c18d612907245e809ddd24f76291/src/vs/workbench/contrib/tasks/common/taskConfiguration.ts#L1135-L1136


class CommandProperties(BaseModel):
    """
    Dataclass for a list of configs based on the OS
    """

    # https://github.com/microsoft/vscode/blob/e0c332665ce059efebb4477a90dd62e3aadcd688/src/vs/workbench/contrib/tasks/common/taskConfiguration.ts#L266-L282

    windows: Optional[BaseCommandProperties] = None
    linux: Optional[BaseCommandProperties] = None
    osx: Optional[BaseCommandProperties] = None

    @property
    def os(self) -> Union[BaseCommandProperties, None]:
        """
        Get the OS option for the current OS
        """
        if PLATFORM_KEY == "windows":
            return self.windows
        elif PLATFORM_KEY == "linux":
            return self.linux
        elif PLATFORM_KEY == "osx":
            return self.osx
