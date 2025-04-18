import subprocess
import sys
import threading
from typing import Dict, List, Optional

import vscode_task_runner.helpers
import vscode_task_runner.printer
import vscode_task_runner.variables
from vscode_task_runner.task import Task


def execute_task(
    task: Task,
    index: int,
    total: int,
    input_vars_values: Optional[Dict[str, str]] = None,
    default_build_task: Optional[str] = None,
    extra_args: Optional[List[str]] = None,
    color_index: int = 0,
) -> None:
    """
    Execute a given task. A 1-based index and total number of tasks must be provided
    for printing.

    Args:
        task: The task to execute
        index: 1-based index of the task in the sequence
        total: Total number of tasks
        input_vars_values: Input variables values mapping
        default_build_task: Label of the default build task if any
        extra_args: Extra arguments to pass to the task
        color_index: Index used for color coding output
    """
    if task.is_virtual:
        vscode_task_runner.printer.info(
            f"[{index}/{total}] Task {vscode_task_runner.printer.yellow(task.label)} has no direct command to execute"
        )
        return

    # Initialize empty dict if input_vars_values is None
    vars_values = input_vars_values or {}

    cmd = vscode_task_runner.variables.replace_runtime_variables(
        task.subprocess_command(extra_args), vars_values, default_build_task
    )

    with vscode_task_runner.printer.group(f"Task {task.label}"):
        vscode_task_runner.printer.info(
            f"[{index}/{total}] Executing task {vscode_task_runner.printer.yellow(task.label)}: {vscode_task_runner.printer.blue(vscode_task_runner.helpers.combine_string(cmd))}"
        )

        # Use task_output_context for output formatting with task labels
        with vscode_task_runner.printer.task_output_context(task.label, color_index):
            # Create pipes for output redirection
            proc = subprocess.Popen(
                cmd,
                shell=False,
                cwd=task.cwd,
                env=task.env,
                stdout=subprocess.PIPE,  # Capture stdout instead of directing to sys.stdout
                stderr=subprocess.PIPE,  # Capture stderr instead of directing to sys.stderr
                bufsize=1,  # Line buffered
                text=True,  # Use text mode
            )

            # Process output in real-time and redirect through context manager's streams
            while proc.poll() is None:
                # Read stdout
                stdout_line = proc.stdout.readline() if proc.stdout else ""
                if stdout_line:
                    print(stdout_line.rstrip())

                # Read stderr
                stderr_line = proc.stderr.readline() if proc.stderr else ""
                if stderr_line:
                    print(stderr_line.rstrip(), file=sys.stderr)

            # Get any remaining output after process completes
            stdout_remainder = proc.stdout.read() if proc.stdout else ""
            if stdout_remainder:
                print(stdout_remainder.rstrip())

            stderr_remainder = proc.stderr.read() if proc.stderr else ""
            if stderr_remainder:
                print(stderr_remainder.rstrip(), file=sys.stderr)

            return_code = proc.returncode
            proc = subprocess.CompletedProcess(cmd, return_code, None, None)

        if proc.returncode != 0:
            vscode_task_runner.printer.error(
                f"Task {vscode_task_runner.printer.yellow(task.label)} returned with exit code {proc.returncode}"
            )
            sys.exit(proc.returncode)


def execute_task_thread(
    task: Task,
    index: int,
    total: int,
    input_vars_values: Optional[Dict[str, str]] = None,
    default_build_task: Optional[str] = None,
    extra_args: Optional[List[str]] = None,
    color_index: int = 0,
) -> None:
    """
    Execute a task in a thread. Used for parallel execution.

    Args:
        task: The task to execute
        index: 1-based index of the task in the sequence
        total: Total number of tasks
        input_vars_values: Input variables values mapping
        default_build_task: Label of the default build task if any
        extra_args: Extra arguments to pass to the task
        color_index: Index used for color coding output
    """
    try:
        # Apply task output context to prefix all output with the task name
        with vscode_task_runner.printer.task_output_context(task.label, color_index):
            execute_task(
                task, index, total, input_vars_values, default_build_task, extra_args
            )
    except Exception as e:
        vscode_task_runner.printer.error(
            f"Task {vscode_task_runner.printer.yellow(task.label)} failed: {str(e)}"
        )
        sys.exit(1)


def collect_task(task: Task, all_tasks: Optional[List[Task]] = None) -> List[Task]:
    """
    Given a task, return the given task and all child tasks, recursively.
    Takes into account dependsOrder.
    """
    if all_tasks is None:
        all_tasks = []

    # Get all dependencies
    dependencies = task.depends_on

    # If no dependencies, just add this task
    if not dependencies:
        all_tasks.append(task)
        return all_tasks

    # Process dependencies based on depends_order
    if task.depends_order == "parallel":
        # For parallel execution, we need to collect all dependencies first
        # recursively, but not run them yet
        for child_task in dependencies:
            # Collect child's dependencies
            collect_task(child_task, all_tasks)
    else:
        # For sequential execution, process dependencies in order
        for child_task in dependencies:
            collect_task(child_task, all_tasks)

    # Add the current task after its dependencies
    all_tasks.append(task)
    return all_tasks


def execute_tasks_parallel(
    tasks: List[Task],
    input_vars_values: Optional[Dict[str, str]] = None,
    default_build_task: Optional[str] = None,
    extra_args: Optional[List[str]] = None,
) -> None:
    """
    Execute a list of tasks in parallel with Docker Compose style output.
    Each line of output will be prefixed with the task name and color-coded.

    Args:
        tasks: List of tasks to execute in parallel
        input_vars_values: Input variables values mapping
        default_build_task: Label of the default build task if any
        extra_args: Extra arguments to pass to the task
    """
    # Print an initial message showing what tasks will run in parallel
    task_names = ", ".join([vscode_task_runner.printer.yellow(t.label) for t in tasks])
    vscode_task_runner.printer.info(f"Running tasks in parallel: {task_names}")

    threads = []
    for i, task in enumerate(tasks):
        thread = threading.Thread(
            target=execute_task_thread,
            args=(
                task,
                i + 1,
                len(tasks),
                input_vars_values,
                default_build_task,
                extra_args,
                i,  # Pass color index based on task index for consistent colors
            ),
        )
        threads.append(thread)
        thread.start()

    # Wait for all tasks to complete
    for thread in threads:
        thread.join()
