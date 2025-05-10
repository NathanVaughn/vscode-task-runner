import os
from typing import Optional, Union

from pydantic import BaseModel, Field, PrivateAttr

from vscode_task_runner.models.enums import ShellTypeEnum
from vscode_task_runner.utils.paths import which_resolver
from vscode_task_runner.variables.resolve import resolve_variables_data


class ShellQuotingOptionsEscape(BaseModel):
    # https://github.com/microsoft/vscode/blob/e0c332665ce059efebb4477a90dd62e3aadcd688/src/vs/workbench/contrib/tasks/common/taskConfiguration.ts#L50-L53
    escape_character: str = Field(alias="escapeChar")
    characters_to_escape: list[str] = Field(alias="charsToEscape")


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

    # https://github.com/microsoft/vscode/blob/f4fb3e71208ebe861a00581c47d2a98bf23f68a2/src/vs/workbench/contrib/tasks/common/jsonSchemaCommon.ts#L58-L75
    _quoting: Optional[ShellQuotingOptions] = PrivateAttr(default=None)
    """
    while appearing in the interface, not something the user can specify
    """
    _type: Optional[ShellTypeEnum] = PrivateAttr(default=None)
    """
    Private attribute to cache the shell type.
    """

    @property
    def type_(self) -> ShellTypeEnum:
        """
        Try to identify what type of shell it is based on the executable.
        """
        if self._type is not None:
            return self._type

        assert self.executable is not None
        shell_executable = which_resolver(self.executable)

        # https://stackoverflow.com/a/41659825
        shell_basename = os.path.basename(shell_executable.replace("\\", os.path.sep))
        shell_basename = shell_basename.removesuffix(".exe")

        # don't check for .exe because it could be running powershell
        # core on Linux
        if shell_basename in ["pwsh", "powershell"]:
            self._type = ShellTypeEnum.PowerShell

        elif shell_basename == "cmd":
            self._type = ShellTypeEnum.CMD

        elif shell_basename == "wsl":
            self._type = ShellTypeEnum.WSL

        # bash.exe is a thing on Windows too
        elif shell_basename.endswith("sh"):
            # this should get zsh, fish, etc
            self._type = ShellTypeEnum.SH

        # anything else
        else:
            self._type = ShellTypeEnum.Unknown

        return self._type

    @property
    def quoting(self) -> Optional[ShellQuotingOptions]:
        """
        Which kind of quotes the shell supports.
        """
        return self._quoting

    @quoting.setter
    def quoting(self, value: Optional[ShellQuotingOptions]) -> None:
        """
        Which kind of quotes the shell supports.
        """
        self._quoting = value

    def resolve_variables(self) -> None:
        """
        Resolve variables for this shell config.
        """
        self.executable = resolve_variables_data(self.executable)
        self.args = resolve_variables_data(self.args)
