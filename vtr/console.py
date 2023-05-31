import argparse
import itertools
import os
from typing import Dict

import vtr.executor
import vtr.json_parser
from vtr.task import Task


def run() -> None:
    task_label_help_text = "One or more task labels to run. This is case sensitive."

    # parse the tasks.json
    try:
        all_tasks_data, tasks_json = vtr.json_parser.load_vscode_tasks_data()
        # build task objects
        all_tasks: Dict[str, Task] = {
            t["label"]: Task(all_tasks_data, t["label"])
            for t in all_tasks_data["tasks"]
            if t.get("type", "process") in ["process", "shell"]
        }
    except FileNotFoundError:
        all_tasks = {}
        task_label_help_text += (
            " Invoke this command inside a directory with a"
            + f" {os.path.join('.vscode', 'tasks.json')} file to see and run tasks."
        )

    parser = argparse.ArgumentParser(description="VS Code Task Runner")
    parser.add_argument(
        "task_labels",
        nargs="+",
        choices=all_tasks.keys(),
        help=task_label_help_text,
    )
    parser.add_argument(
        "--extra-args",
        nargs="*",
        action="append",
        default=[],
        help="When running a single task, extra args to append to that task."
        + " If a single task is requested, but has dependent tasks, only the top-level"
        + " task will be given the extra arguments."
        + ' If the task is a "process" type, then this will be added to "args".'
        + ' If the task is a "shell" type with only a "command" then this will'
        + " be tacked on to the end and joined by spaces."
        + ' If the task is a "shell" type with '
        + ' a "command" and "args", then this will be appended to "args".',
    )
    args = parser.parse_args()

    # the append action makes it come in as a list, but it's the only way
    # to allow multiple --extra-args= flags work
    args.extra_args = list(itertools.chain.from_iterable(args.extra_args))

    if len(args.task_labels) > 1 and args.extra_args:
        parser.error("Extra arguments can only be used with a single task.")

    # filter to tasks explicitly asked for
    top_level_tasks = [all_tasks[t] for t in args.task_labels]

    # get all tasks, following dependencies
    tasks_to_execute = []
    for task in top_level_tasks:
        tasks_to_execute.extend(vtr.executor.collect_task(task))

    # start executing
    for i, task in enumerate(tasks_to_execute):
        extra_args = []
        # top-level task will always be the last one
        if i + 1 == len(tasks_to_execute):
            extra_args = args.extra_args

        vtr.executor.execute_task(
            task, index=i + 1, total=len(tasks_to_execute), extra_args=extra_args
        )


if __name__ == "__main__":
    run()
