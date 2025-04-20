from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr, field_validator

from vscode_task_runner2.models.options import (
    CommandString,
    OSConfigs,
    StringListStringQuotedStringType,
    TaskConfig,
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


class TaskProperties(OSConfigs, TaskConfig):
    """
    Properties of a task.
    These are also availble globally.
    """

    model_config = ConfigDict(extra="allow")

    type_: str = Field(alias="type", default=TaskTypeEnum.process.value)
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

    def new_env_computed(self) -> dict[str, str]:
        """
        Computed explicitly defined environment variables for this task.
        Does not take into account the global environment variables.
        """
        task_env = {}

        if self.options:
            task_env = {**task_env, **self.options.env}
        if self.os and self.os.options:
            task_env = {**task_env, **self.os.options.env}

        return task_env

    def cwd_computed(self) -> Optional[str]:
        """
        Computed working directoy for this task.
        Does not take into account the global working directory.
        """
        cwd = None
        if self.os and self.os.options and self.os.options.cwd:
            cwd = self.os.options.cwd
        elif self.options and self.options.cwd:
            cwd = self.options.cwd

        return cwd

    def command_computed(self) -> Optional[StringListStringQuotedStringType]:
        """
        Computed command for this task.
        Does not take into account the global command.
        """
        command = None
        if self.os and self.os.command:
            command = self.os.command
        elif self.command:
            command = self.command

        return command

    def args_computed(self) -> list[CommandString]:
        """
        Computed args for this task.
        Does not take into account the global args.
        """
        args = []
        if self.os and self.os.args:
            args = self.os.args
        elif self.args:
            args = self.args

        return args


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

    @field_validator("depends_on_labels", mode="before")
    def convert_depends_on_labels(cls, value: Union[str, list[str]]) -> list[str]:
        """
        Convert the depends_on_labels to a list of strings.
        Technically putting a single string is valid.
        """
        return [value] if isinstance(value, str) else value

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
