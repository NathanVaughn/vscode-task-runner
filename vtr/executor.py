import subprocess
import sys
from typing import Dict, List, Optional

import vtr.helpers
import vtr.variables
from vtr.task import Task


def execute_task(
    task: Task,
    index: int,
    total: int,
    input_vars_values: Dict[str, str],
    default_build_task: Optional[str] = None,
    extra_args: Optional[List[str]] = None,
) -> None:
    """
    Execute a given task. A 1-based index and total number of tasks must be provided
    for printing.
    """
    if task.is_virtual:
        vtr.helpers.print2(
            f'[{index}/{total}] Task "{task.label}" has no direct command to execute'
        )
        return

    cmd = vtr.variables.replace_runtime_variables(
        task.subprocess_command(extra_args), input_vars_values, default_build_task
    )

    vtr.helpers.print2(
        f'[{index}/{total}] Executing task "{task.label}": {vtr.helpers.combine_string(cmd)}'
    )
    proc = subprocess.run(cmd, shell=False, cwd=task.cwd, env=task.env)

    if proc.returncode != 0:
        vtr.helpers.print2(
            f'Task "{task.label}" returned with exit code {proc.returncode}'
        )
        sys.exit(proc.returncode)


def collect_task(task: Task, all_tasks: Optional[List[Task]] = None) -> List[Task]:
    """
    Given a task, return the given task and all child tasks, recursively.
    """
    if all_tasks is None:
        all_tasks = []

    for child_task in task.depends_on:
        collect_task(child_task, all_tasks)

    all_tasks.append(task)
    return all_tasks
