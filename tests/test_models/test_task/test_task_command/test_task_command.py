from tests.conftest import task_obj
from vscode_task_runner.models.enums import ShellQuotingEnum
from vscode_task_runner.models.strings import QuotedStringConfig


def test_full(linux: None) -> None:
    task = task_obj(__file__, "cmd-test")

    assert task.command_use() == QuotedStringConfig(
        value="command4", quoting=ShellQuotingEnum.weak
    )


def test_partial1(linux: None) -> None:
    task = task_obj(__file__, "cmd-test")
    task.linux = None

    assert task.command_use() == ["command3"]


def test_partial2(linux: None) -> None:
    task = task_obj(__file__, "cmd-test")
    task.linux = None
    task.command = None

    assert task.command_use() == "command2"


def test_partial3(linux: None) -> None:
    task = task_obj(__file__, "cmd-test")
    task.linux = None
    task.command = None
    task._tasks.linux = None

    assert task.command_use() == "command1"


def test_partial4(linux: None) -> None:
    task = task_obj(__file__, "cmd-test")
    task.linux = None
    task.command = None
    task._tasks.linux = None
    task._tasks.command = None

    assert task.command_use() is None
