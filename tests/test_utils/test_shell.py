import pytest
import shellingham
from pytest_mock import MockerFixture

from vscode_task_runner.exceptions import ShellNotFound
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


@pytest.mark.parametrize(
    "environment_variable",
    [("COMSPEC", "")],
    indirect=True,
)
def test_get_fallback_shell(
    windows: None,
    environment_variable: None,
    detect_shell_patch: None,
    shutil_which_patch: None,
    mocker: MockerFixture,
) -> None:
    """
    Test that fallback shell is used when environment variable is empty
    """
    mocker.patch.object(shell, "FALLBACK_SHELL", "shell.exe")
    assert shell.get_parent_shell() == ShellConfiguration(executable="shell.exe")


@pytest.mark.parametrize(
    "environment_variable",
    [("COMSPEC", "")],
    indirect=True,
)
def test_shell_exception(
    windows: None,
    environment_variable: None,
    detect_shell_patch: None,
    shutil_which_patch: None,
    mocker: MockerFixture,
) -> None:
    """
    Test that exception is raised when everything fails
    """
    mocker.patch.object(shell, "FALLBACK_SHELL", "")
    with pytest.raises(ShellNotFound):
        shell.get_parent_shell()
