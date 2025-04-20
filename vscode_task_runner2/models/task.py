from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from vscode_task_runner2.models.options import (
    CommandOptions,
    OSOptions,
    QuotedStringType,
)

if TYPE_CHECKING:
    from vscode_task_runner2.models.tasks import Tasks


class DependsOrderEnum(str, Enum):
    """
    Enum for task execution order
    """

    parallel = "parallel"
    sequence = "sequence"


class TaskTypeEnum(str, Enum):
    """
    Enum for task types
    """

    process = "process"
    shell = "shell"


class GroupEnum(str, Enum):
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
    is_default: bool = Field(alias="isDefault", default=False)


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
    is_background: bool = Field(alias="isBackground", default=False)
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
    depends_on_labels: list[str] = Field(alias="dependsOn", default_factory=list)
    """
    List of task labels that this task depends on.
    """
    depends_order: DependsOrderEnum = Field(
        alias="dependsOrder", default=DependsOrderEnum.parallel
    )
    """
    Order in which child tasks are executed.
    """

    _depends_on: list[Task] = PrivateAttr(default_factory=list)
    """
    List of task objects that this task depends on.
    This will be set by the parent Tasks object after initialization.
    Must have an underscore to be a private attribute.
    """
    _tasks: Tasks = PrivateAttr()
    """
    Reference to the parent Tasks object.
    This will be set by the parent Tasks object after initialization.
    Must have an underscore to be a private attribute.
    """

    @property
    def depends_on(self) -> list[Task]:
        """
        The list of task objects that this task depends on.
        """
        return self._depends_on

    @property
    def is_default_build_task(self) -> bool:
        return (
            isinstance(self.group, Group)
            and self.group.kind == GroupEnum.build
            and self.group.is_default
        )

    @property
    def is_supported(self) -> bool:
        """
        Check if the task is supported by VTR.
        """
        if self.is_background:
            # bakground tasks are not supported
            return False

        try:
            self.type_enum
        except ValueError:
            # unsupported task type
            return False

        return True
