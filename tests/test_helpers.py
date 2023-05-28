from typing import Any, Type

import pytest

import src.helpers
from src.models import QuotedString, ShellQuoting
from src.typehints import CommandString


@pytest.mark.parametrize(
    "input_, output",
    (
        ("test", "test"),
        (1, "1"),
        (2.0, "2.0"),
        (True, "True"),
    ),
)
def test_stringify_pass(input_: Any, output: str) -> None:
    assert src.helpers.stringify(input_) == output


@pytest.mark.parametrize(
    "input_, exception",
    (
        ({}, ValueError),
        (None, ValueError),
        ({"key": "value"}, ValueError),
    ),
)
def test_stringify_fail(input_: Any, exception: Type[Exception]) -> None:
    with pytest.raises(exception):
        src.helpers.stringify(input_)


@pytest.mark.parametrize(
    "input_, output",
    (("test", "test"), (["te", "st"], "te st")),
)
def test_combine_string(input_: Any, output: str) -> None:
    assert src.helpers.combine_string(input_) == output


@pytest.mark.parametrize(
    "input_, output",
    (
        ("test", "test"),
        (["test"], "test"),
        (["te", "st"], "te st"),
        (
            {"value": "test", "quoting": "escape"},
            QuotedString(value="test", quoting=ShellQuoting.Escape),
        ),
        (
            {"value": ["test"], "quoting": "escape"},
            QuotedString(value="test", quoting=ShellQuoting.Escape),
        ),
        (
            {"value": ["te", "st"], "quoting": "escape"},
            QuotedString(value="te st", quoting=ShellQuoting.Escape),
        ),
    ),
)
def test_load_command_string_pass(input_: Any, output: CommandString) -> None:
    assert src.helpers.load_command_string(input_) == output


@pytest.mark.parametrize(
    "input_, exception",
    (
        ({}, KeyError),
        (None, ValueError),
        ({"key": "value"}, KeyError),
    ),
)
def test_load_command_string_fail(input_: Any, exception: Type[Exception]) -> None:
    with pytest.raises(exception):
        src.helpers.load_command_string(input_)
