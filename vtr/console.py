import argparse

import vtr.executor
import vtr.json_parser
from vtr.task import Task


def run() -> None:
    # parse the tasks.json
    all_tasks_data, tasks_json = vtr.json_parser.load_vscode_tasks_data()

    # build task objects
    all_tasks: dict[str, Task] = {
        t["label"]: Task(all_tasks_data, t["label"])
        for t in all_tasks_data["tasks"]
        if t.get("type") in ["process", "shell"]
    }

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "task_labels",
        nargs="+",
        choices=all_tasks.keys(),
        help="One or more task labels to run. This is case sensitive.",
    )
    args = parser.parse_args()

    # filter to tasks explicitly asked for
    top_level_tasks = [all_tasks[t] for t in args.task_labels]

    # get all tasks, following dependencies
    tasks_to_execute = []
    for task in top_level_tasks:
        tasks_to_execute.extend(vtr.executor.collect_task(task))

    # start executing
    for i, task in enumerate(tasks_to_execute):
        vtr.executor.execute_task(task, index=i + 1, total=len(tasks_to_execute))


if __name__ == "__main__":
    run()
