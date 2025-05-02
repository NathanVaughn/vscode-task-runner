import pytest
import shellingham
from pytest_mock import MockerFixture

from vscode_task_runner.models.shell import ShellConfiguration
from vscode_task_runner.utils import shell


@pytest.fixture
def detect_shell_patch(mocker: MockerFixture) -> None:
    """
    Fixture to always raise a ShellDetectionFailure exception
    """

    def replacement():
        raise shellingham.ShellDetectionFailure

    mocker.patch("shellingham.detect_shell", replacement)


def test_get_parent_shell() -> None:
    """
    Normal
    """
    from vscode_task_runner.utils import shell

    assert shell.get_parent_shell() is not None


@pytest.mark.parametrize(
    "environment_variable",
    [("COMSPEC", "shell.exe")],
    indirect=True,
)
def test_get_parent_shell_windows_comspec(
    windows: None,
    environment_variable: None,
    detect_shell_patch: None,
    shutil_which_patch: None,
) -> None:
    """
    Test that the COMSPEC environment variable is used
    """
    assert shell.get_parent_shell() == ShellConfiguration(executable="shell.exe")


@pytest.mark.parametrize(
    "environment_variable",
    [("SHELL", "/bin/shell")],
    indirect=True,
)
def test_get_parent_shell_linux_shell(
    linux: None,
    environment_variable: None,
    detect_shell_patch: None,
    shutil_which_patch: None,
) -> None:
    """
    Test that the SHELL environment variable is used
    """
    assert shell.get_parent_shell() == ShellConfiguration(executable="/bin/shell")
