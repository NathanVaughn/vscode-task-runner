import shutil
from pathlib import Path

from vscode_task_runner.exceptions import ExecutableNotFound


def which_resolver(exec: str, cwd: Path) -> str:
    """
    Resolves a binary to a full path. Raises `ExecutableNotFound`
    if not found.
    """
    # VSCode lets the user prefix the executable name with "./"
    # when a Task is a "process" type.

    # Stupid hack to handle this, because `os.path.join` doesn't
    # handle this in the way we want.
    exec = exec.removeprefix("./")

    # https://docs.python.org/3/library/shutil.html#shutil.which

    # First, check the current directory.
    # If that fails, let shutil.which use the system PATH.
    if which_result := shutil.which(exec, path=cwd):
        return which_result
    elif which_result := shutil.which(exec):
        return which_result
    else:
        raise ExecutableNotFound(f"Executable {exec} not found")
