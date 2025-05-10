import shutil

from vscode_task_runner.exceptions import ExecutableNotFound


def which_resolver(path: str) -> str:
    """
    Resolves a binary to a full path. Raises `ExecutableNotFound`
    if not found.
    """
    if path_result := shutil.which(path):
        return path_result
    else:
        raise ExecutableNotFound(f"Executable {path} not found")
