from typing import Any, Literal, Optional

from pydantic import Field

from vscode_task_runner.models.input import Input
from vscode_task_runner.models.task import Task, TaskProperties
from vscode_task_runner.utils.picker import determine_default_build_task


class Tasks(TaskProperties):
    version: Literal["2.0.0"]
    # we only support version 2.0.0

    tasks: list[Task]
    inputs: list[Input] = Field(default_factory=list)

    @property
    def tasks_dict(self) -> dict[str, Task]:
        """
        Get a dictionary of tasks by their label.
        """
        return {task.label: task for task in self.tasks}

    def default_build_task(self) -> Optional[Task]:
        """
        Get the default build task.
        """
        options = [task for task in self.tasks if task.is_default_build_task()]

        if len(options) > 1:
            # vscode allows you to pick the default build task
            return determine_default_build_task(options)
        elif not options:
            return None
        else:
            return options[0]

    def model_post_init(self, context: Any) -> None:
        """
        This runs automatically after the model is initialized.
        """
        for task in self.tasks:
            # give the task a reference to the parent tasks object
            task._tasks = self

            # convert the depends on task labels to task objects
            for task_label in task.depends_on_labels:
                task._depends_on.append(self.tasks_dict[task_label])
