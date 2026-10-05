import os

import pytest

from vscode_task_runner.exceptions import ExecutableNotFound
from vscode_task_runner.utils.paths import which_resolver


def test_which_resolver() -> None:
    # allow /bin/bash and /usr/bin/bash
    assert which_resolver("bash", "/").endswith("/bin/bash")


def test_which_resolver_local_prefix() -> None:
    assert which_resolver(
        "./hello.sh", os.path.abspath(os.path.dirname(__file__))
    ) == os.path.abspath(os.path.join(os.path.dirname(__file__), "hello.sh"))


def test_which_resolver_fail() -> None:
    with pytest.raises(ExecutableNotFound):
        which_resolver("blahblahblah", "/")
