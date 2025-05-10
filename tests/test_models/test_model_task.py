import pytest

from vscode_task_runner.exceptions import UnsupportedTaskType
from vscode_task_runner.models.enums import TaskTypeEnum
from vscode_task_runner.models.task import Task, TaskProperties


def test_task_properties_type_enum():
    """
    Test parsing of task type to enum.
    """
    assert TaskProperties(type="process").type_enum == TaskTypeEnum.process
    assert TaskProperties(type="shell").type_enum == TaskTypeEnum.shell

    with pytest.raises(UnsupportedTaskType):
        TaskProperties(type="npm").type_enum


def test_task_depends_on():
    """
    Test depends_on method.
    """
    task_1 = Task(label="Task1")
    task_2 = Task(label="Task2")

    task_3 = Task(label="Task3")
    task_3._depends_on = [task_1, task_2]

    assert task_3.depends_on == [task_1, task_2]


def test_task_resolve_variables(default_build_task_mock: None):
    """
    Test resolve_variables method.
    """
    task = Task(label="Task1", command="echo ${defaultBuildTask}")
    task.resolve_variables()

    assert task.command == "echo task1"

    # try to resolve again
    # ensure nothing happen
    assert task._vars_resolved is True
    task.resolve_variables()
    assert task._vars_resolved is True
