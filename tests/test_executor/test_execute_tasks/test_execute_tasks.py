import subprocess

import pytest

from tests.conftest import task_obj
from vscode_task_runner import executor


def test_execute_tasks(subprocess_run_mock: None, shutil_which_patch: None) -> None:
    """
    Test general execution of tasks.
    """
    t1 = task_obj(__file__, "Task1")

    executor.execute_tasks([t1], extra_args=["--help"])

    assert subprocess.run.call_args_list[0].kwargs.get("args") == [
        "echo",
        "I come first",
    ]
    assert subprocess.run.call_args_list[1].kwargs.get("args") == [
        "echo",
        "hello world",
        "--help",
    ]


def test_execute_virtual_tasks(
    subprocess_run_mock: None, shutil_which_patch: None
) -> None:
    """
    Test executing virtual tasks.
    """
    t3 = task_obj(__file__, "Task3")

    executor.execute_tasks([t3], extra_args=[])

    assert subprocess.run.call_args_list[0].kwargs.get("args") == [
        "echo",
        "I come first",
    ]
    assert subprocess.run.call_args_list[1].kwargs.get("args") == [
        "echo",
        "hello world",
    ]


def test_execute_tasks_fail(
    subprocess_run_mock_fail: None, shutil_which_patch: None
) -> None:
    """
    Test executing a task that fails.
    """
    t1 = task_obj(__file__, "Task1")

    with pytest.raises(SystemExit):
        executor.execute_tasks([t1], extra_args=[])

    assert len(subprocess.run.call_args_list) == 1
    assert subprocess.run.call_args_list[0].kwargs.get("args") == [
        "echo",
        "I come first",
    ]
