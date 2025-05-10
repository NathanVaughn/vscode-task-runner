from typing import Any, Union

import pytest
import questionary
from pytest_mock import MockerFixture

from vscode_task_runner.exceptions import UnsupportedInput, UnsupportedVariable
from vscode_task_runner.models.enums import InputTypeEnum
from vscode_task_runner.models.input import Input, InputChoice
from vscode_task_runner.variables import resolve


@pytest.mark.parametrize(
    "environment_variable",
    [("TEST1", "value1")],
    indirect=True,
)
def test_replace_env_variables(environment_variable: None) -> None:
    """
    Test that environment variables are replaced
    """
    assert resolve.replace_env_variables("abc ${env:TEST1} def") == "abc value1 def"


def test_replace_input_variables(mocker: MockerFixture) -> None:
    """
    Test that input variables are replaced
    """

    def replacement(input_id: str) -> str:
        return "value1"

    mocker.patch.object(resolve, "get_input_value", new=replacement)
    assert resolve.replace_input_variables("abc ${input:TEST1} def") == "abc value1 def"


def test_replace_supported_variables(default_build_task_mock: None) -> None:
    """
    Test that supported variables are replaced
    """

    # python versions 3.7+ maintain order
    input_string = (
        " ".join(resolve.SUPPORTED_PREDEFINED_VARIABLES.keys()) + " ${defaultBuildTask}"
    )
    output_string = " ".join(resolve.SUPPORTED_PREDEFINED_VARIABLES.values()) + " task1"

    assert resolve.replace_supported_variables(input_string) == output_string


@pytest.mark.parametrize(
    "text",
    (
        "${workspaceFolder:TEST1}",
        "${config:TEST1}",
        "${command:TEST1}",
    ),
)
def test_check_unsupported_prefixes(text: str) -> None:
    """
    Test that unsupported prefixes raise an exception
    """
    with pytest.raises(UnsupportedVariable):
        resolve.check_unsupported_prefixes(text)


@pytest.mark.parametrize(
    "text",
    # random selection of unsupported variables
    (
        "${extensionInstallFolder}",
        "${lineNumber}",
        "${fileBasename}",
    ),
)
def test_check_unsupported_vars(text: str) -> None:
    """
    Test that unsupported variables raise an exception
    """
    with pytest.raises(UnsupportedVariable):
        resolve.check_unsupported_vars(text)


def test_get_input_value_text(mocker: MockerFixture) -> None:
    """
    Test that input variables that are of type text are requested
    """
    mocker.patch.object(questionary, attribute="text")
    mocker.patch.object(
        resolve,
        "INPUTS",
        new={
            "TEST1": Input(
                id="TEST1", description="Description1", type=InputTypeEnum.promptString
            )
        },
    )

    resolve.get_input_value("TEST1")
    questionary.text.assert_called_once_with("Description1", default="")


def test_get_input_value_password(mocker: MockerFixture) -> None:
    """
    Test that input variables that are of type password are requested
    """
    mocker.patch.object(questionary, attribute="password")
    mocker.patch.object(
        resolve,
        "INPUTS",
        new={
            "TEST2": Input(
                id="TEST2",
                description="Description2",
                type=InputTypeEnum.promptString,
                password=True,
            )
        },
    )

    resolve.get_input_value("TEST2")
    questionary.password.assert_called_once_with("Description2", default="")


def test_get_input_value_select(mocker: MockerFixture) -> None:
    """
    Test that input variables that are of type select are requested
    """
    mocker.patch.object(questionary, attribute="select")
    mocker.patch.object(
        resolve,
        "INPUTS",
        new={
            "TEST3": Input(
                id="TEST3",
                description="Description3",
                type=InputTypeEnum.pickString,
                options=["option1", "option2"],
            )
        },
    )

    resolve.get_input_value("TEST3")
    questionary.select.assert_called_once_with(
        "Description3", choices=["option1", "option2"], default=None
    )


def test_get_input_value_unsupported(mocker: MockerFixture) -> None:
    """
    Test what happens when a command input is provided
    """
    mocker.patch.object(
        resolve,
        "INPUTS",
        new={
            "TEST4": Input(
                id="TEST4",
                description="Description4",
                type=InputTypeEnum.command,
            )
        },
    )

    with pytest.raises(UnsupportedInput):
        resolve.get_input_value("TEST4")


@pytest.mark.parametrize(
    "environment_variable",
    [("VTR_INPUT_TEST5", "value5")],
    indirect=True,
)
def test_get_input_value_env_promptstring(
    environment_variable: None, mocker: MockerFixture
) -> None:
    """
    Test that input variables can be set via env for promptstring
    """
    mocker.patch.object(
        resolve,
        "INPUTS",
        new={
            "TEST5": Input(
                id="TEST5",
                description="Description5",
                type=InputTypeEnum.promptString,
            )
        },
    )

    assert resolve.get_input_value("TEST5") == "value5"


@pytest.mark.parametrize(
    "environment_variable",
    [("VTR_INPUT_TEST6", "option1")],
    indirect=True,
)
def test_get_input_value_env_pickstring(
    environment_variable: None, mocker: MockerFixture
) -> None:
    """
    Test that input variables can be set via env for pickstring
    """
    mocker.patch.object(
        resolve,
        "INPUTS",
        new={
            "TEST6": Input(
                id="TEST6",
                description="Description5",
                type=InputTypeEnum.pickString,
                options=[InputChoice(label="Option 1", value="option1"), "option2"],
            )
        },
    )

    assert resolve.get_input_value("TEST6") == "option1"


@pytest.mark.parametrize(
    "data, expected",
    (
        ("${defaultBuildTask}", "task1"),
        ("blah", "blah"),
        (None, None),
        (["${defaultBuildTask}"], ["task1"]),
        ({"key": "${defaultBuildTask}"}, {"key": "task1"}),
    ),
)
def test_resolve_variables_data(
    data: Union[str, list[str], dict[str, str], None],
    expected: Any,
    default_build_task_mock: None,
) -> None:
    """
    Full end-to-end test of the resolve_variables function
    """
    assert resolve.resolve_variables_data(data) == expected
