import argparse

import vtr.executor
import vtr.json_parser
from vtr.task import Task


def run() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "task_labels",
        nargs="+",
        help="One or more task labels to run. This is case sensitive.",
    )
    args = parser.parse_args()

    # parse the tasks.json
    all_tasks_data, tasks_json = vtr.json_parser.load_vscode_tasks_data()
    # build taks objects
    all_tasks = [
        Task(all_tasks_data, t["label"])
        for t in all_tasks_data["tasks"]
        if t.get("type") in ["process", "shell"]
    ]

    # verify that the tasks requested actually exist
    all_task_labels = [t.label for t in all_tasks]
    if task_labels_not_found := [
        tl for tl in args.task_labels if tl not in all_task_labels
    ]:
        parser.error(
            f"The following tasks could not be found in '{tasks_json}': {', '.join(task_labels_not_found)}"
        )

    # filter to tasks explicitly asked for
    top_level_tasks = [t for t in all_tasks if t.label in args.task_labels]
    # get all tasks, following dependencies
    tasks_to_execute = []
    (
        tasks_to_execute.extend(vtr.executor.collect_task(task))
        for task in top_level_tasks
    )

    # start executing
    for i, task in enumerate(tasks_to_execute):
        vtr.executor.execute_task(task, index=i + 1, total=len(tasks_to_execute))


if __name__ == "__main__":
    run()
