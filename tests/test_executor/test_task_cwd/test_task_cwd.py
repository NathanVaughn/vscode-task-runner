from pathlib import Path

import pytest

from tests.conftest import task_obj
from vscode_task_runner import executor
from vscode_task_runner.exceptions import WorkingDirectoryNotFound


def test_full(linux: None, pathlib_is_dir_true: None) -> None:
    task = task_obj(__file__, "cwd-test")

    assert executor.task_cwd(task) == Path("/value4")


def test_partial2(linux: None, pathlib_is_dir_true: None) -> None:
    task = task_obj(__file__, "cwd-test")
    task.linux = None

    assert executor.task_cwd(task) == Path("/value3")


def test_partial3(linux: None, pathlib_is_dir_true: None) -> None:
    task = task_obj(__file__, "cwd-test")
    task.linux = None
    task._tasks.options = None

    assert executor.task_cwd(task) == Path("/value3")


def test_partial4(linux: None, pathlib_is_dir_true: None) -> None:
    task = task_obj(__file__, "cwd-test")
    task._tasks.options = None

    assert executor.task_cwd(task) == Path("/value4")


def test_partial5(linux: None, pathlib_is_dir_true: None) -> None:
    task = task_obj(__file__, "cwd-test")
    task.options = None
    task.linux = None

    assert executor.task_cwd(task) == Path("/value2")


def test_directroy_not_found() -> None:
    task = task_obj(__file__, "cwd-test")

    with pytest.raises(WorkingDirectoryNotFound):
        executor.task_cwd(task)
