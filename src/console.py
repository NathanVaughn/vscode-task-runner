import argparse

import src.executor
import src.task_parser
from src.task import Task


def run() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "tasks", nargs="+", help="One or more tasks to run based on the label"
    )
    args = parser.parse_args()

    all_tasks_data = src.task_parser.load_vscode_tasks_data()

    for task_label in args.tasks:
        src.executor.execute_task(Task(all_tasks_data, task_label))


if __name__ == "__main__":
    run()
