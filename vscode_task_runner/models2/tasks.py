from typing import Literal

from vscode_task_runner.models2.inputs import Input
from vscode_task_runner.models2.task import Task, TaskProperties


class Tasks(TaskProperties):
    version: Literal["2.0.0"]
    # we only support version 2.0.0

    tasks: list[Task]
    inputs: list[Input]

    def get_task_by_label(self, label: str) -> Task:
        """
        Get a task by its label.
        """

        return next((task for task in self.tasks if task.label == label))
