import argparse
import sys
from typing import List

from vscode_task_runner import executor, printer
from vscode_task_runner.constants import TASKS_FILE
from vscode_task_runner.exceptions import TasksFileNotFound
from vscode_task_runner.models.arg_parser import ArgParseResult
from vscode_task_runner.models.task import TaskTypeEnum
from vscode_task_runner.parser import load_tasks


def parse_args(sys_argv: List[str], task_choices: List[str]) -> ArgParseResult:
    """
    Parse arguments from the command line. Split out as seperate function for testing.
    Returns an object with a list of tasks selected, and extra arguments.
    """

    parser = argparse.ArgumentParser(
        description="VS Code Task Runner",
        epilog="When running a single task, extra args can be appended only to that task."
        + " If a single task is requested, but has dependent tasks, only the top-level"
        + " task will be given the extra arguments."
        + f' If the task is a "{TaskTypeEnum.process.value}" type, then this will be added to "args".'
        + f' If the task is a "{TaskTypeEnum.shell.value}" type with only a "command" then this will'
        + " be tacked on to the end and joined by spaces."
        + f' If the task is a "{TaskTypeEnum.shell.value}" type with '
        + ' a "command" and "args", then this will be appended to "args".',
    )
    parser.add_argument(
        "task_labels",
        nargs="+",
        choices=task_choices,
        help="One or more task labels to run. This is case sensitive.",
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

    return ArgParseResult(task_labels=args.task_labels, extra_args=extra_args)


def run() -> int:
    """
    Run the console application.
    This is the entry point for the console application.
    """

    try:
        tasks = load_tasks()
    except TasksFileNotFound:
        printer.error(
            (
                "Invoke this command inside a directory with a"
                + f" {TASKS_FILE} file to see and run tasks."
            )
        )
        return 1

    # build a list of possible task labels
    task_choices = [task.label for task in tasks.tasks if task.is_supported()]

    # parse the command line arguments
    parse_result = parse_args(sys.argv[1:], task_choices)

    # convert task labels to task objects
    tasks = [tasks.tasks_dict[label] for label in parse_result.task_labels]

    # run
    executor.execute_tasks(
        tasks=tasks,
        extra_args=parse_result.extra_args,
    )

    return 0  # pragma: no cover
