from pydantic import BaseModel

from vscode_task_runner2.models.task import DependsOrderEnum, Task


class ExecutionLevel(BaseModel):
    order: DependsOrderEnum
    tasks: list[Task]
