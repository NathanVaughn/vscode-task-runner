import shutil
import subprocess

from src.task import Task


def execute_shell_task(task: Task) -> None:
    pass


def execute_process_task(task: Task) -> None:
    which_task_command = shutil.which(task.command)

    if not which_task_command:
        raise ValueError(f"Unable to locate {task.command} in PATH")

    subprocess_command = []
    if task.args is not None:
        subprocess_command.extend(task.args)

    subprocess.check_call(subprocess_command, shell=False, cwd=task.cwd, env=task.env)


def execute_task(task: Task) -> None:
    if task.type_ == "process":
        execute_process_task(task)
    elif task.type_ == "shell":
        execute_shell_task(task)
