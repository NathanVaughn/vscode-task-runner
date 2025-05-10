from pytest_mock import MockerFixture

import vscode_task_runner.models.tasks
from tests.conftest import tasks_obj


def test_default_build_task(mocker: MockerFixture) -> None:
    """
    Test that determine_default_build_task is called when there is more than one
    default build task.
    """
    mocker.patch.object(vscode_task_runner.models.tasks, "determine_default_build_task")

    # this along will run default_build_task for the runtime variables
    tasks_obj(__file__)
    vscode_task_runner.models.tasks.determine_default_build_task.assert_called_once()
