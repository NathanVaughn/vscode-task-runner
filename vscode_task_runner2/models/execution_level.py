from pydantic import BaseModel

from vscode_task_runner2.models.task import DependsOrder, Task


class ExecutionLevel(BaseModel):
    order: DependsOrder
    tasks: list[Task]
