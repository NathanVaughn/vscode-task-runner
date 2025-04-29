import pytest

from vscode_task_runner.exceptions import UnsupportedTaskType
from vscode_task_runner.models.enums import TaskTypeEnum
from vscode_task_runner.models.task import TaskProperties


def test_task_properties_type_enum():
    assert TaskProperties(type="process").type_enum == TaskTypeEnum.process
    assert TaskProperties(type="shell").type_enum == TaskTypeEnum.shell

    with pytest.raises(UnsupportedTaskType):
        TaskProperties(type="npm").type_enum
