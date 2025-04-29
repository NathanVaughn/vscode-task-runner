import subprocess
import sys


def test_entrypoint() -> None:
    # make sure nothing errors out
    subprocess.run([sys.executable, "-m", "vscode_task_runner", "--help"], check=True)
