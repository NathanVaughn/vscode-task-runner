import os
import pathlib
from typing import Any, Generator

import pytest
from pytest_mock import MockerFixture

import vscode_task_runner.constants
import vscode_task_runner.utils.shell
import vscode_task_runner.vscode.terminal_task_system
from vscode_task_runner.models.task import Task
from vscode_task_runner.models.tasks import Tasks
from vscode_task_runner.parser import load_tasks

PLATFORM_SOURCES = (
    vscode_task_runner.constants,
    vscode_task_runner.vscode.terminal_task_system,
    vscode_task_runner.utils.shell,
)
"""
Sources where the platform key is used. Need to patch each one.
"""


def _patch_platform(mocker: MockerFixture, platform: str) -> None:
    for source in PLATFORM_SOURCES:
        mocker.patch.object(source, "PLATFORM_KEY", platform)


@pytest.fixture
def windows(mocker: MockerFixture) -> None:
    _patch_platform(mocker, "windows")


@pytest.fixture
def linux(mocker: MockerFixture) -> None:
    _patch_platform(mocker, "linux")


@pytest.fixture
def osx(mocker: MockerFixture) -> None:
    _patch_platform(mocker, "osx")


@pytest.fixture
def shutil_which_patch(mocker: MockerFixture) -> None:
    mocker.patch("shutil.which", new=lambda x: x)


@pytest.fixture
def subprocess_run_patch(mocker: MockerFixture) -> None:
    mocker.patch("subprocess.run", new=lambda x: x)


@pytest.fixture
def environment_variable(request: Any) -> Generator:
    variable = request.param[0]
    value = request.param[1]

    # grab the current environment variable
    original_value = os.environ.get(variable)

    # set it to the desired value
    os.environ[variable] = value

    # run test
    yield

    # reset
    if original_value is not None:
        os.environ[variable] = original_value
    else:
        del os.environ[variable]


@pytest.fixture
def pathlib_is_dir_true(monkeypatch: pytest.MonkeyPatch) -> None:
    def always_true(*args: Any, **kwargs: Any) -> bool:
        return True

    monkeypatch.setattr(pathlib.Path, "is_dir", always_true)


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
