import os
from typing import Any, Generator

import pytest
from pytest_mock import MockerFixture

import vscode_task_runner_old.constants
from vscode_task_runner_old.parser import load_vscode_tasks_data
from vscode_task_runner_old.task import Task
from vscode_task_runner_old.variables import replace_static_variables


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
def windows(mocker: MockerFixture) -> None:
    mocker.patch.object(vscode_task_runner_old.constants, "PLATFORM_KEY", "windows")


@pytest.fixture
def linux(mocker: MockerFixture) -> None:
    mocker.patch.object(vscode_task_runner_old.constants, "PLATFORM_KEY", "linux")


@pytest.fixture
def osx(mocker: MockerFixture) -> None:
    mocker.patch.object(vscode_task_runner_old.constants, "PLATFORM_KEY", "osx")


@pytest.fixture
def shutil_which_patch(mocker: MockerFixture) -> None:
    mocker.patch("shutil.which", new=lambda x: x)


def load_task(path: str, label: str) -> Task:
    """
    Given a working directory and task label, returns the Task object.
    """
    # if the given path is not a directory, remove the last part
    if os.path.isfile(path):
        path = os.path.dirname(path)

    data = replace_static_variables(load_vscode_tasks_data(path))

    return Task(data, label)
