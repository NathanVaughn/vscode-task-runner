from tests2.conftest import task_obj
from vscode_task_runner2 import executor


def test_full(linux: None) -> None:
    task = task_obj(__file__, "arg-test")

    # os-specific
    assert executor.task_args(task) == ["arg7", "arg8"]


def test_partial1(linux: None) -> None:
    task = task_obj(__file__, "arg-test")
    task.linux = None

    # task-specific
    assert executor.task_args(task) == ["arg5", "arg6"]


def test_partial2(linux: None) -> None:
    task = task_obj(__file__, "arg-test")
    task.linux = None
    task.args = []

    # no args when task has none and defines command
    assert executor.task_args(task) == []


def test_partial3(linux: None) -> None:
    task = task_obj(__file__, "arg-test")
    task.linux = None
    task.args = []
    task._tasks.linux = None

    # no args when task defines command
    assert executor.task_args(task) == []


def test_partial4(linux: None) -> None:
    task = task_obj(__file__, "arg-test")
    task._tasks.linux = None

    # check inheritance of task os-specific
    assert executor.task_args(task) == ["arg7", "arg8"]


def test_partial5(linux: None) -> None:
    task = task_obj(__file__, "arg-test")
    task._tasks.linux = None
    task.linux = None

    # check task inheritance
    assert executor.task_args(task) == ["arg5", "arg6"]


def test_partial6(linux: None) -> None:
    task = task_obj(__file__, "arg-test")
    task.args = []
    task.linux = None

    # no args when task defines a command but no args, even with global args
    assert executor.task_args(task) == []


def test_partial7(linux: None) -> None:
    task = task_obj(__file__, "arg-test")
    task.args = []
    task.linux = None
    task._tasks.command = None

    # no args when global command is blank
    assert executor.task_args(task) == []


def test_partial8(linux: None) -> None:
    task = task_obj(__file__, "arg-test")
    task.command = None

    # when task has no command, combine args
    assert executor.task_args(task) == ["arg3", "arg4", "arg7", "arg8"]


def test_partial9(linux: None) -> None:
    task = task_obj(__file__, "arg-test")
    task.command = None
    task.args = []
    task.linux = None

    # when task has no command, no args, use global
    assert executor.task_args(task) == ["arg3", "arg4"]
