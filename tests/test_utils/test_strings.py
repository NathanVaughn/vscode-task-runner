import pytest

from vscode_task_runner.utils.strings import joiner


@pytest.mark.parametrize("input_, output", ((["a", "b", "c"], "a b c"),))
def test_joiner(input_: list[str], output: str) -> None:
    assert joiner(input_) == output
