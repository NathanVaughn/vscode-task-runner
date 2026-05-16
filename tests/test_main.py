import os
import subprocess
import sys

import pytest


def test_entrypoint() -> None:
    # make sure nothing errors out
    subprocess.run([sys.executable, "-m", "vscode_task_runner", "--help"], check=True)


def test_complete_errpr() -> None:
    """
    Test that the error is shown and the program exits when --complete is passed when not in a directory with a tasks file
    """
    cwd = os.getcwd()
    os.chdir(os.path.dirname(__file__))

    try:
        with pytest.raises(subprocess.CalledProcessError):
            subprocess.run(
                [sys.executable, "-m", "vscode_task_runner", "--complete"], check=True
            )

    # rset cwd so it doesn't mess with other tests
    finally:
        os.chdir(cwd)
