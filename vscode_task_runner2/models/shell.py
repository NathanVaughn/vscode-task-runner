import os
from typing import Optional, Union

from pydantic import BaseModel, Field

from vscode_task_runner2.models.enums import ShellTypeEnum
from vscode_task_runner2.utils.paths import which_resolver
from vscode_task_runner2.variables import resolve_variables_data


class ShellQuotingOptionsEscape(BaseModel):
    # https://github.com/microsoft/vscode/blob/e0c332665ce059efebb4477a90dd62e3aadcd688/src/vs/workbench/contrib/tasks/common/taskConfiguration.ts#L50-L53
    escape_character: str = Field(alias="escapeChar")
    characters_to_escape: list[str] = Field(alias="charsToEscape")

    def resolve_variables(self) -> None:
        self.escape_character = resolve_variables_data(self.escape_character)
        self.characters_to_escape = resolve_variables_data(self.characters_to_escape)


class ShellQuotingOptions(BaseModel):
    """
    Shell quoting options
    """

    # https://github.com/microsoft/vscode/blob/e0c332665ce059efebb4477a90dd62e3aadcd688/src/vs/workbench/contrib/tasks/common/taskConfiguration.ts#L46-L64

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

    def resolve_variables(self) -> None:
        self.strong = resolve_variables_data(self.strong)

        if isinstance(self.escape, ShellQuotingOptionsEscape):
            self.escape.resolve_variables()
        else:
            self.escape = resolve_variables_data(self.escape)

        self.weak = resolve_variables_data(self.weak)


class ShellConfiguration(BaseModel):
    """
    Shell configuration settings
    """

    # https://github.com/microsoft/vscode/blob/e0c332665ce059efebb4477a90dd62e3aadcd688/src/vs/workbench/contrib/tasks/common/taskConfiguration.ts#L66-L70

    executable: Optional[str] = None
    """
    The shell executable.
    """
    # not using a FilePath to allow for missing paths on not all platforms
    args: list[str] = Field(default_factory=list)
    """
    The args to be passed to the shell executable.
    """
    quoting: Optional[ShellQuotingOptions] = None
    """
    Which kind of quotes the shell supports.
    """

    @property
    def type_(self) -> ShellTypeEnum:
        """
        Try to identify what type of shell it is based on the executable.
        """
        assert self.executable is not None
        shell_executable = which_resolver(self.executable)

        # https://stackoverflow.com/a/41659825
        shell_basename = os.path.basename(shell_executable.replace("\\", os.path.sep))
        shell_basename.removesuffix(".exe")

        # don't check for .exe because it could be running powershell
        # core on Linux
        if shell_basename in ["pwsh", "powershell"]:
            return ShellTypeEnum.PowerShell

        elif shell_basename == "cmd":
            return ShellTypeEnum.CMD

        elif shell_basename == "wsl":
            return ShellTypeEnum.WSL

        # bash.exe is a thing on Windows too
        elif shell_basename.endswith("sh"):
            return ShellTypeEnum.SH

        return ShellTypeEnum.Unknown

    def resolve_variables(self) -> None:
        self.executable = resolve_variables_data(self.executable)
        self.args = resolve_variables_data(self.args)

        if self.quoting:
            self.quoting.resolve_variables()
