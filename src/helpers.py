import os
import shutil

import dacite
import shellingham

from src.constants import PLATFORM_KEY
from src.models import QuotedString, ShellConfiguration, ShellQuoting, ShellType
from src.typehints import CommandString


def identify_shell_type(shell_executable: str) -> ShellType:
    """
    Try to identify what type of shell it is based on the executable.
    """
    shell_executable_which = shutil.which(shell_executable)
    if shell_executable_which is None:
        raise FileNotFoundError(f"Shell executable {shell_executable} not found")

    shell_executable = shell_executable_which
    shell_basename = os.path.basename(shell_executable)

    # don't check for .exe because it could be running powershell
    # core on Linux
    if any(i in shell_basename for i in ("pwsh", "powershell")):
        return ShellType.PowerShell

    if shell_basename == "cmd.exe":
        return ShellType.CMD

    if shell_basename == "wsl.exe":
        return ShellType.WSL

    # bash.exe is a thing on Windows too
    return ShellType.SH


def get_parent_shell() -> ShellConfiguration:
    """
    Returns the full path to the parent shell, and the arguments needed
    to launch a command.
    """

    # try to get the path to the parent shell
    try:
        name, shell_executable = shellingham.detect_shell()
    except shellingham.ShellDetectionFailure:
        shell_executable = None

    # if path is none or empty
    if not shell_executable:
        # use SHELL variable
        if PLATFORM_KEY != "windows":
            shell_executable = os.environ.get("SHELL")
            # default to /bin/sh
            if not shell_executable or not shutil.which(shell_executable):
                shell_executable = "/bin/sh"

        # use COMSPEC variable
        elif PLATFORM_KEY == "windows":
            shell_executable = os.environ.get("COMSPEC")
            # default to cmd.exe
            if not shell_executable or not shutil.which(shell_executable):
                shell_executable = os.path.join(
                    os.environ.get("SystemRoot", ""), "System32", "cmd.exe"
                )

    # make sure we found SOMETHING
    if not shell_executable:
        raise FileNotFoundError("A shell could not be found")

    # just make sure path is fully resolved
    shell_executable = shutil.which(shell_executable)

    # path could not be resolved
    if not shell_executable:
        raise FileNotFoundError("A shell could not be found")

    return ShellConfiguration(executable=shell_executable)


def stringify(value: str | int | float | bool) -> str:
    """
    Make sure the incoming value is close enough to a string, and convert it.
    """

    if not isinstance(value, (str, int, float, bool)):
        raise ValueError(f"Value '{value}' is not a string/number/boolean")

    return str(value)


def combine_string(value: str | list[str]) -> str:
    """
    Given either a single string, or list of string, return a single string.
    A list will be joined by spaces.
    """
    if isinstance(value, str):
        return value

    assert all(isinstance(i, str) for i in value)
    return " ".join(value)


def load_command_string(data: dict | str | list[str]) -> CommandString:
    """
    Given data, either return the string, or loads into a the QuotedString dataclass.
    """
    if isinstance(data, (str, list)):
        return combine_string(data)

    elif isinstance(data, dict):
        data["value"] = combine_string(data["value"])

        return dacite.from_dict(
            data_class=QuotedString,
            data=data,
            config=dacite.Config(cast=[ShellQuoting]),
        )
    else:
        raise ValueError("Invalid command string data type")
