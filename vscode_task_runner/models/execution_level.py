from pydantic import BaseModel

from vscode_task_runner.models.task import DependsOrderEnum, Task


class ExecutionLevel(BaseModel):
    """
    Data class to represent the tasks that need to be run and in what order.
    """

    order: DependsOrderEnum
    tasks: list[Task]
