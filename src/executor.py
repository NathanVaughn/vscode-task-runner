import subprocess
import sys

import src.helpers
from src.task import Task


def execute_task(task: Task) -> None:
    cmd = task.subprocess_command

    print(f"Executing: {src.helpers.combine_string(cmd)}")
    proc = subprocess.run(cmd, shell=False, cwd=task.cwd, env=task.env)

    if proc.returncode != 0:
        print(f"Task {task.label} returned with exit code {proc.returncode}")
        sys.exit(proc.returncode)
