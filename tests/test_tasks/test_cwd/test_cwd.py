import os

import pytest

from tests.conftest import load_task


def test_default(linux: None) -> None:
    # test that default value is used
    task = load_task(__file__, "Test")
    assert task.cwd == os.getcwd()


def test_check(windows: None) -> None:
    # test that an invalid directory is rejected
    task = load_task(__file__, "Test")
    with pytest.raises(ValueError):
        task.cwd  # noqa
