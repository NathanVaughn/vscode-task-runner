import argparse
import dataclasses
import os
import sys
from typing import Dict, List

import vscode_task_runner_old.executor
import vscode_task_runner_old.parser
import vscode_task_runner_old.variables
from vscode_task_runner_old.exceptions import TasksFileNotFound
from vscode_task_runner_old.models import TaskType
from vscode_task_runner_old.task import Task


@dataclasses.dataclass
class ParseResult:
    task_labels: List[str]
    extra_args: List[str]


def parse_args(
    sys_argv: List[str], task_choices: List[str], help_text: str
) -> ParseResult:
    """
    Parse arguments from the command line. Split out as seperate function for testing.
    Returns an object with a list of tasks selected, and extra arguments.
    """

    parser = argparse.ArgumentParser(
        description="VS Code Task Runner",
        epilog="When running a single task, extra args can be appended only to that task."
        + " If a single task is requested, but has dependent tasks, only the top-level"
        + " task will be given the extra arguments."
        + f' If the task is a "{TaskType.process.value}" type, then this will be added to "args".'
        + f' If the task is a "{TaskType.process.value}" type with only a "command" then this will'
        + " be tacked on to the end and joined by spaces."
        + f' If the task is a "{TaskType.process.value}" type with '
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
    task_label_help_text = "One or more task labels to run. This is case sensitive."

    # parse the tasks.json
    try:
        all_tasks_data = vscode_task_runner_old.parser.load_vscode_tasks_data()
        all_tasks_data = vscode_task_runner_old.variables.replace_static_variables(
            all_tasks_data
        )

        # build task objects
        all_tasks: Dict[str, Task] = {
            t["label"]: Task(all_tasks_data, t["label"])
            for t in all_tasks_data["tasks"]
        }

        # remove unsupported tasks
        all_tasks = {k: v for k, v in all_tasks.items() if not v.is_invalid}

    except TasksFileNotFound:
        all_tasks = {}
        task_label_help_text += (
            " Invoke this command inside a directory with a"
            + f" {os.path.join('.vscode', 'tasks.json')} file to see and run tasks."
        )

    parse_result = parse_args(
        sys.argv[1:], list(all_tasks.keys()), task_label_help_text
    )

    # filter to tasks explicitly asked for
    top_level_tasks = [all_tasks[t] for t in parse_result.task_labels]

    # get all tasks, following dependencies
    tasks_to_execute: List[Task] = []
    for task in top_level_tasks:
        tasks_to_execute.extend(vscode_task_runner_old.executor.collect_task(task))

    # build list of commands
    # filter out virtual tasks
    all_commands = [
        t.subprocess_command() for t in tasks_to_execute if not t.is_virtual
    ]

    # get dict of input variables and values
    input_vars_values = vscode_task_runner_old.variables.get_input_variables_values(
        all_commands, all_tasks_data.get("inputs")
    )

    # find the default build task
    default_build_task = next(
        (t.label for t in tasks_to_execute if t.is_default_build_task), None
    )

    # start executing
    for i, task in enumerate(tasks_to_execute):
        i_extra_args = []
        # top-level task will always be the last one
        if i + 1 == len(tasks_to_execute):
            i_extra_args = parse_result.extra_args

        vscode_task_runner_old.executor.execute_task(
            task,
            index=i + 1,
            total=len(tasks_to_execute),
            input_vars_values=input_vars_values,
            default_build_task=default_build_task,
            extra_args=i_extra_args,
        )


if __name__ == "__main__":
    run()
