import os
from typing import Optional, Union

from pydantic import BaseModel

from vscode_task_runner2.models.enums import ShellType
from vscode_task_runner2.utils.paths import which_resolver


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

    executable: Optional[str] = None
    """
    The shell executable.
    """
    # not using a FilePath to allow for missing paths on not all platforms
    args: Optional[list[str]] = None
    """
    The args to be passed to the shell executable.
    """
    quoting: Optional[ShellQuotingOptions] = None
    """
    Which kind of quotes the shell supports.
    """

    def shell_type(self) -> ShellType:
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
            return ShellType.PowerShell

        elif shell_basename == "cmd":
            return ShellType.CMD

        elif shell_basename == "wsl":
            return ShellType.WSL

        # bash.exe is a thing on Windows too
        elif shell_basename.endswith("sh"):
            return ShellType.SH

        return ShellType.Unknown
