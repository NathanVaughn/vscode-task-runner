"""Main entry point for the VS Code Task Runner command-line interface."""

import argparse
import dataclasses
import os
import sys
from typing import Dict, List

import vscode_task_runner.parser
import vscode_task_runner.printer
import vscode_task_runner.variables
from vscode_task_runner.exceptions import TasksFileNotFound
from vscode_task_runner.task import Task
from vscode_task_runner.task_executor import TaskExecutor


@dataclasses.dataclass
class ParseResult:
    """Result of command-line argument parsing."""

    task_labels: List[str]
    extra_args: List[str]


def parse_args(
    sys_argv: List[str], task_choices: List[str], help_text: str
) -> ParseResult:
    """
    Parse arguments from the command line.

    Args:
        sys_argv: Command line arguments to parse
        task_choices: List of available task labels
        help_text: Help text to display

    Returns:
        ParseResult with task labels and extra arguments
    """
    parser = argparse.ArgumentParser(
        description="VS Code Task Runner",
        epilog="When running a single task, extra args can be appended only to that task."
        + " If a single task is requested, but has dependent tasks, only the top-level"
        + " task will be given the extra arguments."
        + ' If the task is a "process" type, then this will be added to "args".'
        + ' If the task is a "shell" type with only a "command" then this will'
        + " be tacked on to the end and joined by spaces."
        + ' If the task is a "shell" type with '
        + ' a "command" and "args", then this will be appended to "args".',
    )
    parser.add_argument(
        "task_labels",
        nargs="+",
        choices=task_choices,
        help=help_text,
    )

    # https://stackoverflow.com/a/40686614/9944427
    # https://github.com/NathanVaughn/vscode-task-runner/issues/51
    if "--" in sys_argv:
        break_point = sys_argv.index("--")
        sys_argv_to_parse, extra_extra_args = (
            sys_argv[:break_point],
            sys_argv[break_point + 1 :],
        )
    else:
        sys_argv_to_parse = sys_argv
        extra_extra_args = []

    # parse with argparse
    args, extra_args = parser.parse_known_args(sys_argv_to_parse)
    # combine with items we parsed beforehand
    extra_args = extra_args + extra_extra_args

    if len(args.task_labels) > 1 and extra_args:
        parser.error("Extra arguments can only be used with a single task.")

    return ParseResult(task_labels=args.task_labels, extra_args=extra_args)


def run() -> None:
    """
    Main entry point for the VS Code Task Runner.

    Parses tasks from tasks.json and executes requested tasks respecting
    dependencies and execution order.
    """
    task_label_help_text = "One or more task labels to run. This is case sensitive."

    # parse the tasks.json
    try:
        all_tasks_data = vscode_task_runner.parser.load_vscode_tasks_data()
        all_tasks_data = vscode_task_runner.variables.replace_static_variables(
            all_tasks_data
        )

        # build task objects
        all_tasks: Dict[str, Task] = {
            t["label"]: Task(all_tasks_data, t["label"])
            for t in all_tasks_data["tasks"]
            if t.get("type", "process") in ["process", "shell"]
        }

        # Get inputs data in the correct format
        inputs_data = all_tasks_data.get("inputs", [])
        if not isinstance(inputs_data, list):
            inputs_data = []

    except TasksFileNotFound:
        all_tasks = {}
        inputs_data = []
        task_label_help_text += (
            " Invoke this command inside a directory with a"
            + f" {os.path.join('.vscode', 'tasks.json')} file to see and run tasks."
        )

    parse_result = parse_args(
        sys.argv[1:], list(all_tasks.keys()), task_label_help_text
    )

    # filter to tasks explicitly asked for
    top_level_tasks = [all_tasks[t] for t in parse_result.task_labels]

    # Create task executor
    task_executor = TaskExecutor()

    # Process each top-level task separately
    for top_task in top_level_tasks:
        # Build the dependency tree for the task
        task_tree = task_executor.build_dependency_tree(top_task)

        # Execute the task tree
        task_executor.execute_tree(
            task_tree,
            inputs_data,
            parse_result.extra_args if len(top_level_tasks) == 1 else None,
        )


if __name__ == "__main__":
    run()
