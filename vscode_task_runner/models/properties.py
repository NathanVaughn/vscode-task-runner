from typing import Optional, Union

from pydantic import BaseModel, Field

from vscode_task_runner.constants import PLATFORM_KEY
from vscode_task_runner.models.options import CommandOptions
from vscode_task_runner.models.strings import CommandStringConfig, QuotedStringConfig
from vscode_task_runner.variables.resolve import resolve_variables_data


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

    def resolve_variables(self) -> None:
        """
        Resolve variables for these base command properties.
        """

        # update command
        if isinstance(self.command, QuotedStringConfig):
            self.command.resolve_variables()
        else:
            self.command = resolve_variables_data(self.command)

        # update options
        if self.options:
            self.options.resolve_variables()

        # update args
        new_args = []
        for arg in self.args:
            if isinstance(arg, QuotedStringConfig):
                arg.resolve_variables()
            else:
                arg = resolve_variables_data(arg)
            new_args.append(arg)

        self.args = new_args


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

    def resolve_variables(self) -> None:
        """
        Resolve variables for these command properties.
        """
        if self.os:
            # don't need to do all OS's
            self.os.resolve_variables()
