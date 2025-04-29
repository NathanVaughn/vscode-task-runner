from tests.conftest import task_obj
from vscode_task_runner import executor
from vscode_task_runner.models.shell import ShellConfiguration


def test_full(linux: None, shutil_which_patch: None) -> None:
    task = task_obj(__file__, "shell-test")

    # task os-specific
    assert executor.task_shell(task) == ShellConfiguration(executable="bash")


def test_partial1(linux: None, shutil_which_patch: None) -> None:
    task = task_obj(__file__, "shell-test")
    task.linux = None

    # task-specific
    assert executor.task_shell(task) == ShellConfiguration(executable="python")


def test_partial2(linux: None, shutil_which_patch: None) -> None:
    task = task_obj(__file__, "shell-test")
    task.linux = None
    task.options = None

    # global os-specific
    assert executor.task_shell(task) == ShellConfiguration(executable="pwsh")


def test_partial3(linux: None, shutil_which_patch: None) -> None:
    task = task_obj(__file__, "shell-test")
    task.linux = None
    task.options = None
    task._tasks.linux = None

    # global
    assert executor.task_shell(task) == ShellConfiguration(executable="cmd")


def test_partial4(linux: None, shutil_which_patch: None) -> None:
    task = task_obj(__file__, "shell-test")
    task.linux = None
    task.options = None
    task._tasks.linux = None
    task._tasks.options = None

    # nothing defined, paernt shell is used
    assert executor.task_shell(task) is not None
