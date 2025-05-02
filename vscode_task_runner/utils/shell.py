import os
import shutil

import shellingham

from vscode_task_runner.constants import PLATFORM_KEY
from vscode_task_runner.exceptions import ShellNotFound
from vscode_task_runner.models.shell import ShellConfiguration
from vscode_task_runner.utils.paths import which_resolver

# shell of last resort
if PLATFORM_KEY == "windows":
    FALLBACK_SHELL = os.path.join(  # pragma: no cover
        os.environ.get("SystemRoot", "C:\\Windows"), "System32", "cmd.exe"
    )
else:
    FALLBACK_SHELL = "/bin/sh"  # pragma: no cover


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
        if PLATFORM_KEY == "windows":
            # use COMSPEC variable
            shell_executable = os.environ.get("COMSPEC")
        else:
            # or use SHELL variable
            shell_executable = os.environ.get("SHELL")

        # if those didn't work or set to paths that don't exist,
        # fallback
        if not shell_executable or not shutil.which(shell_executable):
            shell_executable = FALLBACK_SHELL

    # make sure we found SOMETHING
    if not shell_executable:
        raise ShellNotFound("A shell could not be found")

    # just make sure path is fully resolved
    return ShellConfiguration(executable=which_resolver(shell_executable))
