import pytest

from vscode_task_runner.exceptions import ExecutableNotFound
from vscode_task_runner.utils.paths import which_resolver


def test_which_resolver() -> None:
    assert which_resolver("bash")


def test_which_resolver_fail() -> None:
    with pytest.raises(ExecutableNotFound):
        which_resolver("blahblahblah")
