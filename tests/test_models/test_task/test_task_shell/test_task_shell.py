from tests.conftest import task_obj
from vscode_task_runner.models.shell import ShellConfiguration


def test_full(linux: None, shutil_which_patch: None) -> None:
    task = task_obj(__file__, "shell-test")

    # task os-specific
    assert task.shell_use() == ShellConfiguration(executable="bash")


def test_partial1(linux: None, shutil_which_patch: None) -> None:
    task = task_obj(__file__, "shell-test")
    task.linux = None

    # task-specific
    assert task.shell_use() == ShellConfiguration(executable="python")


def test_partial2(linux: None, shutil_which_patch: None) -> None:
    task = task_obj(__file__, "shell-test")
    task.linux = None
    task.options = None

    # global os-specific
    assert task.shell_use() == ShellConfiguration(executable="pwsh")


def test_partial3(linux: None, shutil_which_patch: None) -> None:
    task = task_obj(__file__, "shell-test")
    task.linux = None
    task.options = None
    task._tasks.linux = None

    # global
    assert task.shell_use() == ShellConfiguration(executable="cmd")


def test_partial4(linux: None, shutil_which_patch: None) -> None:
    task = task_obj(__file__, "shell-test")
    task.linux = None
    task.options = None
    task._tasks.linux = None
    task._tasks.options = None

    # nothing defined, paernt shell is used
    assert task.shell_use() is not None
