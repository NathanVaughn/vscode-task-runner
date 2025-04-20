import os

import pytest
from pytest_mock import MockerFixture

import vscode_task_runner2.constants
from vscode_task_runner2.models.task import Task
from vscode_task_runner2.models.tasks import Tasks
from vscode_task_runner2.parser import load_tasks


@pytest.fixture
def windows(mocker: MockerFixture) -> None:
    mocker.patch.object(vscode_task_runner2.constants, "PLATFORM_KEY", "windows")


@pytest.fixture
def linux(mocker: MockerFixture) -> None:
    mocker.patch.object(vscode_task_runner2.constants, "PLATFORM_KEY", "linux")


@pytest.fixture
def osx(mocker: MockerFixture) -> None:
    mocker.patch.object(vscode_task_runner2.constants, "PLATFORM_KEY", "osx")


@pytest.fixture
def shutil_which_patch(mocker: MockerFixture) -> None:
    mocker.patch("shutil.which", new=lambda x: x)


def tasks_obj(path: str) -> Tasks:
    """
    Given a working directory, returns the Tasks object.
    """
    # if the given path is not a directory, remove the last part
    if os.path.isfile(path):
        path = os.path.dirname(path)

    return load_tasks(path)


def task_obj(path: str, label: str) -> Task:
    """
    Given a working directory and task label, returns the Task object.
    """
    return tasks_obj(path).tasks_dict[label]
