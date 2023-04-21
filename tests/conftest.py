import os
from typing import Any, Generator

import pytest
from pytest_mock import MockerFixture

import src.constants
from src.task import Task
from src.task_parser import load_vscode_tasks_data


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
    mocker.patch.object(src.constants, "PLATFORM_KEY", "windows")


@pytest.fixture
def linux(mocker: MockerFixture) -> None:
    mocker.patch.object(src.constants, "PLATFORM_KEY", "linux")


@pytest.fixture
def osx(mocker: MockerFixture) -> None:
    mocker.patch.object(src.constants, "PLATFORM_KEY", "osx")


def load_task(path: str, label: str) -> Task:
    # if the given path is not a directory, remove the last part
    if os.path.isfile(path):
        path = os.path.dirname(path)

    data = load_vscode_tasks_data(path)

    return Task(data, label)
