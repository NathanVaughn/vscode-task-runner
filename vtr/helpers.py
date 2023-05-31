import os
import shutil
from typing import List, Union

import dacite
import shellingham

import vtr.constants
from vtr.models import (
    CommandString,
    QuotedString,
    ShellConfiguration,
    ShellQuoting,
    ShellType,
)


def identify_shell_type(shell_executable: str) -> ShellType:
    # sourcery skip: assign-if-exp, reintroduce-else
    """
    Try to identify what type of shell it is based on the executable.
    """
    shell_executable_which = shutil.which(shell_executable)
    if shell_executable_which is None:
        raise FileNotFoundError(f"Shell executable {shell_executable} not found")

    shell_executable = shell_executable_which

    # https://stackoverflow.com/a/41659825
    shell_basename = os.path.basename(shell_executable.replace("\\", os.path.sep))
    if shell_basename.endswith(".exe"):
        # .removesuffix is only available 3.9+
        shell_basename = shell_basename[:-4]

    # don't check for .exe because it could be running powershell
    # core on Linux
    if shell_basename in ["pwsh", "powershell"]:
        return ShellType.PowerShell

    if shell_basename == "cmd":
        return ShellType.CMD

    if shell_basename == "wsl":
        return ShellType.WSL

    # bash.exe is a thing on Windows too
    if shell_basename.endswith("sh"):
        return ShellType.SH

    return ShellType.Unknown


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
        # use COMSPEC variable
        if vtr.constants.PLATFORM_KEY == "windows":
            shell_executable = os.environ.get("COMSPEC")
            # default to cmd.exe
            if not shell_executable or not shutil.which(shell_executable):
                shell_executable = os.path.join(
                    os.environ.get("SystemRoot", ""), "System32", "cmd.exe"
                )
        # use SHELL variable
        else:
            shell_executable = os.environ.get("SHELL")
            # default to /bin/sh
            if not shell_executable or not shutil.which(shell_executable):
                shell_executable = "/bin/sh"

    # make sure we found SOMETHING
    if not shell_executable:
        raise FileNotFoundError("A shell could not be found")

    # just make sure path is fully resolved
    if shell_executable := shutil.which(shell_executable):
        return ShellConfiguration(executable=shell_executable)
    else:
        raise FileNotFoundError("A shell could not be found")


def stringify(value: Union[str, int, float, bool]) -> str:
    """
    Make sure the incoming value is close enough to a string, and convert it.
    """

    if not isinstance(value, (str, int, float, bool)):
        raise ValueError(f"Value '{value}' is not a string/number/boolean")

    return str(value)


def combine_string(value: Union[str, List[str]]) -> str:
    """
    Given either a single string, or list of string, return a single string.
    A list will be joined by spaces.
    """
    if isinstance(value, str):
        return value

    assert all(isinstance(i, str) for i in value)
    return " ".join(value)


def load_command_string(data: Union[dict, str, List[str]]) -> CommandString:
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
