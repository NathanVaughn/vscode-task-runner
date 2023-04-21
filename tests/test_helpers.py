from typing import Any

import pytest

import src.helpers


@pytest.mark.parametrize(
    "input_, output",
    (
        ("test", "test"),
        (1, "1"),
        (2.0, "2.0"),
        (True, "True"),
        ({}, ValueError),
        (None, ValueError),
        ({"key": "value"}, ValueError),
    ),
)
def test_stringify(input_: Any, output: str | ValueError) -> None:
    if not isinstance(output, str):
        with pytest.raises(ValueError):
            src.helpers.stringify(input_)
    else:
        assert src.helpers.stringify(input_) == output
