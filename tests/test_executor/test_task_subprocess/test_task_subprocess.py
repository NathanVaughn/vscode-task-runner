import pytest

from tests.conftest import task_obj
from vscode_task_runner import executor
from vscode_task_runner.exceptions import MissingCommand


@pytest.mark.parametrize(
    "label, expected",
    [
        (
            "1",
            ["echo", "hello world"],
        ),
        (
            "2",
            ["bash", "-c", "echo 'hello world'"],
        ),
    ],
)
def test_task_subprocess_command(
    label: str, expected: list[str], shutil_which_patch: None
) -> None:
    task = task_obj(__file__, label)

    assert executor.task_subprocess_command(task) == expected


@pytest.mark.parametrize(
    "label, expected",
    [
        (
            "1",
            ["echo", "hello world", "--verbose"],
        ),
        (
            "2",
            ["bash", "-c", "echo 'hello world' --verbose"],
        ),
        (
            "3",
            ["bash", "-c", "echo 'hello world' --verbose"],
        ),
        (
            "4",
            ["bash", "-c", "\"echo 'hello world' --verbose\""],
        ),
    ],
)
def test_task_subprocess_command_extra_args(
    label: str, expected: list[str], shutil_which_patch: None
) -> None:
    task = task_obj(__file__, label)

    assert executor.task_subprocess_command(task, extra_args=["--verbose"]) == expected


def test_task_subprocess_command_no_command(
    shutil_which_patch: None,
) -> None:
    task = task_obj(__file__, "5")

    with pytest.raises(MissingCommand):
        executor.task_subprocess_command(task)
