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
    exec_stripped = exec.removeprefix("./")
    local_only = exec_stripped != exec

    # https://docs.python.org/3/library/shutil.html#shutil.which

    # First, check the current directory.
    # If that fails, let shutil.which use the system PATH.
    if which_result := shutil.which(exec_stripped, path=cwd):
        return which_result
    # Don't allow global search if the "./" prefix was applied
    elif (not local_only) and (which_result := shutil.which(exec_stripped)):
        return which_result
    else:
        raise ExecutableNotFound(f"Executable {exec} not found")
