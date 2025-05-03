from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Union

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    PrivateAttr,
    field_validator,
    model_validator,
)

from vscode_task_runner.exceptions import UnsupportedTaskType, WorkingDirectoryNotFound
from vscode_task_runner.models.enums import (
    DependsOrderEnum,
    GroupKindEnum,
    TaskTypeEnum,
)
from vscode_task_runner.models.properties import (
    BaseCommandProperties,
    CommandProperties,
)
from vscode_task_runner.models.shell import ShellConfiguration
from vscode_task_runner.models.strings import CommandStringConfig
from vscode_task_runner.utils.paths import which_resolver
from vscode_task_runner.utils.shell import get_parent_shell

if TYPE_CHECKING:
    from vscode_task_runner.models.tasks import Tasks  # pragma: no cover


class GroupKind(BaseModel):
    """
    Group model.
    """

    # https://github.com/microsoft/vscode/blob/e0c332665ce059efebb4477a90dd62e3aadcd688/src/vs/workbench/contrib/tasks/common/taskConfiguration.ts#L284-L287

    kind: Optional[GroupKindEnum] = None
    is_default: Union[bool, str] = Field(alias="isDefault", default=False)


class TaskProperties(CommandProperties, BaseCommandProperties):
    """
    Properties of a task.
    These are also availble globally.
    """

    model_config = ConfigDict(extra="allow")

    type_: str = Field(alias="type", default=TaskTypeEnum.process.value)
    group: Optional[Union[GroupKindEnum, GroupKind]] = None
    """
    Group of the task
    """
    is_background: Optional[bool] = Field(alias="isBackground", default=None)
    """
    If the task is a background task
    """

    @property
    def type_enum(self) -> TaskTypeEnum:
        try:
            return TaskTypeEnum(self.type_)
        except ValueError as e:
            raise UnsupportedTaskType(f"Unsupported task type {self.type_}") from e

    def new_env_os(self) -> dict[str, str]:
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

    def cwd_os(self) -> Optional[str]:
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

    def command_os(self) -> Optional[CommandStringConfig]:
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

    def args_os(self) -> list[CommandStringConfig]:
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

    def shell_os(self) -> Optional[ShellConfiguration]:
        """
        Computed shell for this task.
        Does not take into account the global shell.
        """
        shell = None

        if self.os and self.os.options and self.os.options.shell:
            shell = self.os.options.shell
        elif self.options and self.options.shell:
            shell = self.options.shell

        return shell


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
    _vars_resolved: bool = PrivateAttr(default=False)
    """
    Keep track if this item has already had variables resolved.
    """

    @field_validator("depends_on_labels", mode="before")
    def process_depends_on_labels(cls, value: Union[str, list[str]]) -> list[str]:
        """
        Convert the depends_on_labels to a list of strings.
        Putting a single string is valid.
        Additionally, make sure that the list is unique and preserve the order.
        """
        new_value = [value] if isinstance(value, str) else value
        return list(dict.fromkeys(new_value))

    @model_validator(mode="after")
    def check_depends_on_labels(self) -> Task:
        """
        Ensure the depends_on_labels are unique and not self-referencing.
        """
        # check for self-reference
        if self.label in self.depends_on_labels:
            raise ValueError("Task cannot depend on itself")

        return self

    # =======
    # Properties

    @property
    def depends_on(self) -> list[Task]:
        """
        The list of task objects that this task depends on.
        """
        return self._depends_on

    # =======
    # Computed items

    def is_default_build_task(self) -> bool:
        """
        Check if this task is the default build task.
        """
        group = self.group_use()
        return (
            isinstance(group, GroupKind)
            and group.kind == GroupKindEnum.build
            and group.is_default is True
        )

    def is_supported(self) -> bool:
        """
        Check if the task is supported.
        """
        try:
            self.type_enum
        except UnsupportedTaskType:
            # unsupported task type
            return False

        if self.is_background_use():
            # background tasks are not supported
            return False

        return True

    def is_background_use(self) -> bool:
        # sourcery skip: assign-if-exp, boolean-if-exp-identity, reintroduce-else
        """
        Return if this task is a background task.
        """
        # if this task explicitly sets it, then return that value
        if self.is_background is not None:
            return self.is_background

        # if this task uses the global command (by not having one),
        # and the global command is set to background, then return True
        if self.command_os() is None and self._tasks.is_background:
            return True

        return False

    def group_use(self) -> Optional[Union[GroupKindEnum, GroupKind]]:
        """
        Return the group for this task.
        """
        group = None

        # task settings
        if self.group:
            group = self.group

        # global settings
        elif global_group := self._tasks.group:
            group = global_group

        return group

    def _new_env(self) -> dict[str, str]:
        """
        Return the explicitly defined environment variables for this task.
        """
        # VSCode will merge environment variables for os-independent options
        # and os-specific options. It will not merge the environment variables
        # from the global configuration to the task-specific configuration.
        # if the task defines options.

        global_tasks_env = self._tasks.new_env_os()
        task_env = self.new_env_os()

        # if the task defined any of its own options, discard global
        # otherwise, return the global task environment
        return task_env or global_tasks_env

    def env_use(self) -> dict[str, str]:
        """
        Rreturn the environment variables to set for this task.
        """
        task_env = self._new_env()
        # combine with a copy of the current environment
        return {**os.environ.copy(), **task_env}

    def cwd_use(self) -> Path:
        """
        Return the working directory to to use for this task.
        """
        cwd = Path(os.getcwd())

        # vscode treats cwd as an absolute path
        # this works as well on windows to define the root directory
        # this still works because an absolute joined to an absolute path
        # will yield the joined absolute path
        # pathlib.Path("/tmp").joinpath("/var") -> Path("/var/")
        base = Path("/")

        # task settings
        if task_cwd := self.cwd_os():
            cwd = base.joinpath(task_cwd)

        # global settings
        elif global_cwd := self._tasks.cwd_os():
            cwd = base.joinpath(global_cwd)

        if not cwd.is_dir():
            raise WorkingDirectoryNotFound(f"Working directory {cwd} does not exist")

        return cwd

    def command_use(self) -> Optional[CommandStringConfig]:
        """
        Return the command to use for this task.
        """
        command = None

        # task settings
        if task_command := self.command_os():
            command = task_command

        # global settings
        elif global_command := self._tasks.command_os():
            command = global_command

        return command

    def args_use(self) -> list[CommandStringConfig]:
        """
        Return the arguments to pass to the command for this task.
        """
        global_args = self._tasks.args_os()
        task_args = self.args_os()

        # in the case that there is a global command defined, but not a task
        # command, tack on the task args to the global args
        task_command = self.command_os()
        return global_args + task_args if task_command is None else task_args

    def shell_use(self) -> ShellConfiguration:
        """
        Return the shell configuration to use for this task.
        """
        shell = ShellConfiguration()

        # task settings
        if task_shell := self.shell_os():
            shell = task_shell

        # global settings
        elif global_shell := self._tasks.shell_os():
            shell = global_shell

        if not shell.executable:
            # if no shell binary defined, use the parent shell
            shell = get_parent_shell()

        # make sure shell executable exists and is absolute
        assert shell.executable is not None
        shell.executable = which_resolver(shell.executable)

        # return the shell config
        return shell

    # =======
    # variables

    def resolve_variables(self) -> None:
        """
        Resolve variables in this Task
        """
        if self._vars_resolved:
            # prevent duplicates
            return

        # need to do this because of mixins
        CommandProperties.resolve_variables(self)
        BaseCommandProperties.resolve_variables(self)

        # record what we did
        self._vars_resolved = True
