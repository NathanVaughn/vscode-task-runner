import argparse
import os
import sys
from typing import List

import colorama

from vscode_task_runner import executor, printer
from vscode_task_runner.constants import TASKS_FILE
from vscode_task_runner.exceptions import TasksFileNotFound
from vscode_task_runner.models.arg_parser import ArgParseResult
from vscode_task_runner.models.task import Task, TaskTypeEnum
from vscode_task_runner.parser import load_tasks
from vscode_task_runner.variables.runtime import INPUTS

_COMPLETE_FLAG = "--complete"
_SKIP_SUMMARY_FLAG = "--skip-summary"
_CONTINUE_ON_ERROR_FLAG = "--continue-on-error"


def parse_args(sys_argv: List[str], task_choices: List[str]) -> ArgParseResult:
    """
    Parse arguments from the command line. Split out as seperate function for testing.
    Returns an object with a list of tasks selected, and extra arguments.
    """

    parser = argparse.ArgumentParser(
        description="VS Code Task Runner",
        epilog="Input values can be provided via --input-<id>=<value> flags (can be repeated)."
        + "\n\n"
        + "When running a single task, extra args can be appended only to that task."
        + " If a single task is requested, but has dependent tasks, only the top-level"
        + " task will be given the extra arguments."
        + f' If the task is a "{TaskTypeEnum.process.value}" type, then this will be added to "args".'
        + f' If the task is a "{TaskTypeEnum.shell.value}" type with only a "command" then this will'
        + " be tacked on to the end and joined by spaces."
        + f' If the task is a "{TaskTypeEnum.shell.value}" type with '
        + ' a "command" and "args", then this will be appended to "args".',
    )

    parser.add_argument(
        _SKIP_SUMMARY_FLAG,
        action="store_true",
        help="Skip creating a CI/CD step summary.",
    )

    parser.add_argument(
        _CONTINUE_ON_ERROR_FLAG,
        action="store_true",
        help="Continue executing tasks even if one fails. The final exit code will be 1 if any task failed.",
    )

    parser.add_argument(
        "--list-inputs",
        action="store_true",
        help="List all inputs required by the specified task(s) and exit.",
    )

    parser.add_argument(
        "task_labels",
        nargs="+",
        choices=task_choices,
        help="One or more task labels to run. This is case sensitive.",
    )

    # show list of tasks and exit
    # parse this manually, since normally task labels are required and to make it faster
    if _COMPLETE_FLAG in sys_argv:
        print("\n".join([_SKIP_SUMMARY_FLAG, _CONTINUE_ON_ERROR_FLAG, *task_choices]))
        sys.exit(0)

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

    # parse --input-<id>=<value> flags from extra_args
    input_values = {}
    remaining_extra_args = []

    for arg in extra_args:
        if arg.startswith("--input-"):
            # Handle --input-id=value
            if "=" not in arg:
                parser.error(
                    f"Invalid input flag format: {arg}. Expected: --input-<id>=<value>"
                )
            key_part = arg[8:]  # Remove "--input-" prefix
            input_id, value = key_part.split("=", 1)
            input_values[input_id] = value
        else:
            remaining_extra_args.append(arg)

    extra_args = remaining_extra_args

    if len(args.task_labels) > 1 and extra_args:
        parser.error("Extra arguments can only be used with a single task.")

    # manually set environment variable for ourself
    if args.skip_summary:
        os.environ["VTR_SKIP_SUMMARY"] = "1"

    if args.continue_on_error:
        os.environ["VTR_CONTINUE_ON_ERROR"] = "1"

    return ArgParseResult(
        task_labels=args.task_labels,
        extra_args=extra_args,
        input_values=input_values,
        list_inputs=args.list_inputs,
    )


def set_input_environment_variables(input_values: dict[str, str]) -> None:
    """
    Set VTR_INPUT_* environment variables from CLI arguments.

    CLI arguments take precedence over existing environment variables.

    Args:
        input_values: Dictionary mapping input IDs to values
    """
    for input_id, value in input_values.items():
        env_var_name = f"VTR_INPUT_{input_id}"
        os.environ[env_var_name] = value


def collect_task_inputs(tasks: list[Task]) -> set[str]:
    """
    Collect all input IDs referenced in tasks and their dependencies.

    Args:
        tasks: List of tasks to scan for input references

    Returns:
        Set of input IDs found in the tasks
    """
    import re

    input_ids: set[str] = set()

    # Build the task order to include all dependencies
    levels = executor.build_tasks_order(tasks)
    all_tasks = [task for level in levels for task in level]

    # Pattern to match ${input:id}
    pattern = re.compile(r"\$\{input:([^}]+)\}")

    # Scan all task properties for input references
    for task in all_tasks:
        # Convert task to dict to scan all string properties
        task_dict = task.model_dump()

        # Recursively scan for input references
        def scan_value(value):  # type: ignore
            if isinstance(value, str):
                matches = pattern.findall(value)
                input_ids.update(matches)
            elif isinstance(value, dict):
                for v in value.values():
                    scan_value(v)
            elif isinstance(value, list):
                for item in value:
                    scan_value(item)

        scan_value(task_dict)

    return input_ids


def display_inputs(input_ids: set[str]) -> None:
    """
    Display information about the specified inputs.

    Args:
        input_ids: Set of input IDs to display
    """
    if not input_ids:
        printer.info("No inputs required for the specified task(s).")
        return

    printer.info("Available inputs for the specified task(s):\n")

    sorted_ids = sorted(input_ids)
    for input_id in sorted_ids:
        if input_id not in INPUTS:
            printer.info(f"  {printer.red(input_id)}: (not defined)")
            continue

        input_obj = INPUTS[input_id]

        # Print input ID and type
        printer.info(f"  {printer.blue(input_id)}:")
        printer.info(f"    Type: {input_obj.type_.value}")

        # Print description if available
        if input_obj.description:
            printer.info(f"    Description: {input_obj.description}")

        # Print default if available
        if input_obj.default is not None:
            printer.info(f"    Default: {input_obj.default}")

        # Print options for pickString
        if input_obj.options:
            printer.info("    Options:")
            for option in input_obj.options:
                if isinstance(option, str):
                    printer.info(f"      - {option}")
                else:
                    # InputChoice object
                    printer.info(f"      - {option.value} ({option.label})")

        # Show usage example
        printer.info(f"    Usage: --input-{input_id}=<value>\n")


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
    task_objects = [tasks.tasks_dict[label] for label in parse_result.task_labels]

    # if --list-inputs is set, display inputs and exit
    if parse_result.list_inputs:
        input_ids = collect_task_inputs(task_objects)
        display_inputs(input_ids)
        return 0

    # set input environment variables from CLI args
    set_input_environment_variables(parse_result.input_values)

    # run
    return executor.execute_tasks(
        tasks=task_objects,
        extra_args=parse_result.extra_args,
    )
