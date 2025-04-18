from enum import Enum
from typing import TYPE_CHECKING, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from vscode_task_runner.models2.options import (
    CommandOptions,
    OSOptions,
    QuotedStringType,
)

if TYPE_CHECKING:
    from vscode_task_runner.models2.tasks import Tasks


class DependsOrderEnum(Enum, str):
    """
    Enum for task execution order
    """

    parallel = "parallel"
    sequence = "sequence"


class TaskTypeEnum(Enum, str):
    """
    Enum for task types
    """

    process = "process"
    shell = "shell"


class GroupEnum(Enum, str):
    """
    Enum for task groups
    """

    build = "build"
    test = "test"
    none = "none"


class Group(BaseModel):
    """
    Group model.
    """

    kind: Optional[GroupEnum] = None
    isDefault: bool = False


class TaskProperties(OSOptions):
    """
    Properties of a task.
    These are also availble globally.
    """

    model_config = ConfigDict(extra="allow")

    type_: str = Field(alias="type", default=TaskTypeEnum.process.value)

    command: Optional[QuotedStringType] = None
    args: Optional[list[QuotedStringType]] = None
    options: Optional[CommandOptions] = None
    """
    Options for this task.
    """
    group: Optional[Union[GroupEnum, Group]] = None
    """
    Group of the task
    """
    isBackground: bool = False
    """
    If the task is a background task
    """

    @property
    def type_enum(self) -> TaskTypeEnum:
        return TaskTypeEnum(self.type_)


class Task(TaskProperties):
    """
    Task model.
    """

    label: str
    """
    Unique label for this task.
    """
    dependsOn: Optional[list[str]] = Field(default_factory=list)
    """
    List of task labels that this task depends on.
    """
    dependsOrder: DependsOrderEnum = DependsOrderEnum.parallel
    """
    Order in which child tasks are executed.
    """

    @property
    def is_default_build_task(self) -> bool:
        return (
            isinstance(self.group, Group)
            and self.group.kind == GroupEnum.build
            and self.group.isDefault
        )

    @property
    def tasks(self) -> Tasks:
        return self._tasks

    @tasks.setter
    def tasks(self, tasks: Tasks):
        self._tasks = tasks
