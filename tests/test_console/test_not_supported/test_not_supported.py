import os

import pytest
from pytest import CaptureFixture
from pytest_mock import MockerFixture

from vscode_task_runner.console import run


def test_child_not_suppoted(capsys: CaptureFixture, mocker: MockerFixture) -> None:
    """
    Test selecting a task that has child tasks that are not supported
    """
    # mock sys.argv to simulate running the console
    mocker.patch("sys.argv", ["vscode_task_runner", "Task3"])

    current_cwd = os.getcwd()
    os.chdir(os.path.dirname(__file__))

    # should fail since task depends on a child task that is not supported
    with pytest.raises(SystemExit):
        run()

    os.chdir(current_cwd)
