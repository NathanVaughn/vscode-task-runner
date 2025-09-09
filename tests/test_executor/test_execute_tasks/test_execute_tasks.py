import os
import subprocess

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


def test_execute_tasks_single_ask(
    subprocess_run_mock: None, shutil_which_patch: None
) -> None:
    """
    Test general execution of tasks, with a single task.
    """
    t2 = task_obj(__file__, "Task2")

    executor.execute_tasks([t2], extra_args=[])

    assert subprocess.run.call_args_list[0].kwargs.get("args") == [
        "echo",
        "I come first",
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

    assert executor.execute_tasks([t1], extra_args=[]) == 1
    # make sure only the first task was attempted
    assert len(subprocess.run.call_args_list) == 1
    assert subprocess.run.call_args_list[0].kwargs.get("args") == [
        "echo",
        "I come first",
    ]


def test_execute_tasks_continue_on_errror(
    subprocess_run_mock_fail: None, shutil_which_patch: None
) -> None:
    """
    Test executing tasks with continue_on_error set to true.
    """
    os.environ["VTR_CONTINUE_ON_ERROR"] = "1"

    t1 = task_obj(__file__, "Task1")

    assert executor.execute_tasks([t1], extra_args=[]) == 1
    # make sure both tasks were attempted
    assert len(subprocess.run.call_args_list) == 2
    assert subprocess.run.call_args_list[0].kwargs.get("args") == [
        "echo",
        "I come first",
    ]
    assert subprocess.run.call_args_list[1].kwargs.get("args") == [
        "echo",
        "hello world",
    ]

    del os.environ["VTR_CONTINUE_ON_ERROR"]
