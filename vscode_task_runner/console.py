import os
import shutil
import sys
import textwrap
from typing import List

import colorama

from vscode_task_runner import executor, printer
from vscode_task_runner.constants import TASKS_FILE
from vscode_task_runner.exceptions import TasksFileNotFound
from vscode_task_runner.models.arg_parser import ArgParseResult
from vscode_task_runner.models.task import TaskTypeEnum
from vscode_task_runner.parser import load_tasks

_COMPLETE_FLAG = "--complete"
_SKIP_SUMMARY_FLAG = "--skip-summary"
_CONTINUE_ON_ERROR_FLAG = "--continue-on-error"
_INPUT_FLAG_PREFIX = "--input="
_DEFAULT_BUILD_TASK_FLAG_PREFIX = "--default-build-task="


def parse_args(sys_argv: List[str], task_choices: List[str]) -> ArgParseResult:
    """
    Parse arguments from the command line. Split out as seperate function for testing.
    Returns an object with a list of tasks selected, and extra arguments.
    """

    # structure is:
    # [options] task1 [task2] [--] [extra args]

    options: list[str] = []
    task_labels: list[str] = []
    extra_args: list[str] = []

    # first, go through the args, and find first argument found that is a task label
    # everything before that is an option, everything after that (except for --) is either a task label or an extra arg
    task_label_index = next(
        (i for i, arg in enumerate(sys_argv) if arg in task_choices),
        None,
    )

    # if no task label is found, then all arguments must be options
    if task_label_index is None:
        options = sys_argv
    else:
        options = sys_argv[:task_label_index]
        remaining_args = sys_argv[task_label_index:]

        # go through remaining args until we find an arg that starts with "--"
        # that is not a task label, this is the start of extra args
        for i, arg in enumerate(remaining_args):
            if arg in task_choices:
                task_labels.append(arg)
            elif arg.startswith("--"):
                extra_args = remaining_args[i:]
                break
            else:
                printer.error(f"Invalid task label: {arg}")
                sys.exit(1)

    # remove "--" from extra args if it exists
    if extra_args and extra_args[0] == "--":
        extra_args = extra_args[1:]

    if "-h" in options or "--help" in options:
        # show help message and exit
        task_labels_str = ",".join(task_choices)
        main_msg = f"""
usage: vtr [-h] [{_SKIP_SUMMARY_FLAG}] [{_CONTINUE_ON_ERROR_FLAG}] [{_DEFAULT_BUILD_TASK_FLAG_PREFIX}TASK] [{_INPUT_FLAG_PREFIX}ID=VALUE ...] {{{task_labels_str}}} [{{{task_labels_str}}} ...]

VS Code Task Runner

positional arguments:
{{{task_labels_str}}}
                      One or more task labels to run. This is case sensitive.

options:
-h, --help            Show this help message and exit
{_SKIP_SUMMARY_FLAG}        Skip creating a CI/CD step summary
{_CONTINUE_ON_ERROR_FLAG}   Continue executing tasks even if one fails. The final exit code will be 1 if any task failed.
"""
        # last line is the longest, so try to word wrap it to fit in the terminal
        last_line = f'When running a single task, extra args can be appended only to that task. If a single task is requested, but has dependent tasks, only the top-level task will be given the extra arguments. If the task is a "{TaskTypeEnum.process.value}" type, then this will be added to "args". If the task is a "{TaskTypeEnum.shell.value}" type with only a "command" then this will be tacked on to the end and joined by spaces. If the task is a "{TaskTypeEnum.shell.value}" type with a "command" and "args", then this will be appended to "args".'
        msg = (
            main_msg
            + "\n"
            + textwrap.fill(last_line, width=shutil.get_terminal_size().columns)
        )

        print(msg)
        sys.exit(0)

    # parse options
    for option in options:
        if option == _COMPLETE_FLAG:
            # show list of tasks and exit
            # parse this manually, since normally task labels are required and to make it faster
            print(
                "\n".join([_SKIP_SUMMARY_FLAG, _CONTINUE_ON_ERROR_FLAG, *task_choices])
            )
            sys.exit(0)

        # manually set environment variable for ourself
        elif option == _SKIP_SUMMARY_FLAG:
            os.environ["VTR_SKIP_SUMMARY"] = "1"

        elif option == _CONTINUE_ON_ERROR_FLAG:
            os.environ["VTR_CONTINUE_ON_ERROR"] = "1"

        elif option.startswith(_DEFAULT_BUILD_TASK_FLAG_PREFIX):
            os.environ["VTR_DEFAULT_BUILD_TASK"] = option.removeprefix(
                _DEFAULT_BUILD_TASK_FLAG_PREFIX
            )

        # parse inputs
        elif option.startswith(_INPUT_FLAG_PREFIX):
            # should be in format of
            # --input=TEST1=value

            data = option.removeprefix(_INPUT_FLAG_PREFIX)
            chunks = data.split("=", maxsplit=1)
            if len(chunks) != 2:
                printer.error(f"Invalid option: {option}")
                sys.exit(1)

            os.environ[f"VTR_INPUT_{chunks[0]}"] = chunks[1]

        else:
            printer.error(f"Invalid option: {option}")
            sys.exit(1)

    # finally, validate that at least one task label is provided, and that extra args are only used with a single task
    if not task_labels:
        printer.error("At least one task label is required.")
        sys.exit(1)

    if len(task_labels) > 1 and extra_args:
        printer.error("Extra arguments can only be used with a single task.")
        sys.exit(1)

    return ArgParseResult(task_labels=task_labels, extra_args=extra_args)


def run() -> int:
    """
    Run the console application.
    This is the entry point for the console application.
    """
    colorama.just_fix_windows_console()

    sys_argv = sys.argv[1:]

    try:
        tasks = load_tasks()
    except TasksFileNotFound:
        if _COMPLETE_FLAG not in sys_argv:
            # don't want to provide any output if just completing
            printer.error(
                (
                    "Invoke this command inside a directory with a "
                    + f"{TASKS_FILE} file to see and run tasks."
                )
            )
        return 1

    # build a list of possible task labels
    task_choices = [task.label for task in tasks.tasks if task.is_supported()]

    # parse the command line arguments
    parse_result = parse_args(sys_argv, task_choices)

    # convert task labels to task objects
    tasks = [tasks.tasks_dict[label] for label in parse_result.task_labels]

    # run
    return executor.execute_tasks(
        tasks=tasks,
        extra_args=parse_result.extra_args,
    )
