from typing import Any, Literal

from vscode_task_runner2.models.inputs import Input
from vscode_task_runner2.models.task import Task, TaskProperties


class Tasks(TaskProperties):
    version: Literal["2.0.0"]
    # we only support version 2.0.0

    tasks: list[Task]
    inputs: list[Input]

    def model_post_init(self, context: Any) -> None:
        """
        Convert depends on task labels to task objects.
        """
        for task in self.tasks:
            for task_label in task.depends_on_labels:
                task.depends_on.append(self.get_task_by_label(task_label))

    def get_task_by_label(self, label: str) -> Task:
        """
        Get a task by its label.
        """

        return next((task for task in self.tasks if task.label == label))
