import os
import re
from functools import cache
from typing import Optional, Union, overload

import questionary

from vscode_task_runner.exceptions import (
    ResponseNotProvided,
    UnsupportedInput,
    UnsupportedVariable,
)
from vscode_task_runner.models.input import InputChoice, InputTypeEnum
from vscode_task_runner.utils.picker import check_item_with_options
from vscode_task_runner.variables.runtime import INPUTS, RUNTIME_VARIABLES
from vscode_task_runner.variables.static import (
    SUPPORTED_PREDEFINED_VARIABLES,
    UNSUPPORTED_PREDEFINED_VARIABLES,
)


@cache
def get_input_value(input_id: str) -> str:
    """
    Given an input ID, prompt the user for the input value and return it.
    """
    input_ = INPUTS[input_id]

    # allow the user to provide the input value via environment variable
    if env_value := os.environ.get(f"VTR_INPUT_{input_.id}"):
        if input_.type_ == InputTypeEnum.promptString:
            # if just a prompt string, return the value
            return env_value
        elif input_.type_ == InputTypeEnum.pickString:
            # if a pickstring, make sure the value is one of the options
            # convert options to strings
            options = []
            for option in input_.options:
                if isinstance(option, InputChoice):
                    options.append(option.value)
                else:
                    options.append(option)

            # ensure the environment variable matches one of the options
            check_item_with_options(env_value, options)
            return env_value

    # otherwise, obtain from user input
    if input_.type_ == InputTypeEnum.promptString:
        question_type = questionary.text

        if input_.password is True:
            question_type = questionary.password

        # for prompt string, default cannot be none, but an empty string
        if input_.default is None:
            input_.default = ""

        question = question_type(input_.description, default=input_.default)

    elif input_.type_ == InputTypeEnum.pickString:
        # if the value should be picked from options
        choices: list[Union[str, questionary.Choice]] = []

        # if the options are strings, add them as is
        # otherwise, add them as questionary.Choice
        for option in input_.options:
            if isinstance(option, InputChoice):
                # hard to test since memory addresses will be different
                choices.append(  # pragma: no cover
                    questionary.Choice(title=option.label, value=option.value)
                )
            else:
                choices.append(option)

        question = questionary.select(
            input_.description,
            choices=choices,
            default=input_.default,
        )

    else:
        raise UnsupportedInput(f"Unsupported input variable type '{input_.type_}'")

    output: Optional[str] = question.ask()
    if output is None:
        raise ResponseNotProvided("No response provided")  # pragma: no cover

    return output


def check_unsupported_vars(data: str) -> None:
    """
    Check a string for unsupported variables
    """
    for var in UNSUPPORTED_PREDEFINED_VARIABLES:
        if var in data:
            raise UnsupportedVariable(f"Unsupported variable '{var}'")


def check_unsupported_prefixes(data: str) -> None:
    """
    Check a string for unsupported variable prefixes
    """
    prefixes = ["workspaceFolder", "config", "command"]
    for prefix in prefixes:
        pattern = "\\${" + prefix + ":(.+?)}"
        matches = re.findall(pattern, data)
        for match in matches:
            raise UnsupportedVariable(f"Unsupported variable '{prefix}:{match}'")


def replace_supported_variables(data: str) -> str:
    """
    Replaces references to supported variables in a string with their values.
    """
    for var, value in SUPPORTED_PREDEFINED_VARIABLES.items():
        data = data.replace(var, value)

    for var, value in RUNTIME_VARIABLES.items():
        data = data.replace(var, value)

    return data


def replace_input_variables(data: str) -> str:
    """
    Replaces references to input variables in a string with their values.
    """
    pattern = "\\${input:(.+?)}"
    matches = re.findall(pattern, data)
    for match in matches:
        data = data.replace(f"${{input:{match}}}", get_input_value(input_id=match))

    return data


def replace_env_variables(data: str) -> str:
    """
    Replaces references to environment variables in a string with their values.
    """
    pattern = "\\${env:(.+?)}"
    matches = re.findall(pattern, data)
    for match in matches:
        data = data.replace(f"${{env:{match}}}", os.environ[match])

    return data


@overload
def resolve_variables_data(data: str) -> str: ...
@overload
def resolve_variables_data(data: list[str]) -> list[str]: ...
@overload
def resolve_variables_data(data: dict[str, str]) -> dict[str, str]: ...
@overload
def resolve_variables_data(data: None) -> None: ...
def resolve_variables_data(
    data: Union[str, list[str], dict[str, str], None],
) -> Union[str, list[str], dict[str, str], None]:
    """
    Resolve variables in given data (str, list of strings, dict)
    """
    if data is None:
        return None

    if isinstance(data, str):
        # checks for unsupported things which could be catastrophic
        check_unsupported_vars(data)
        check_unsupported_prefixes(data)

        # main data replacements
        data = replace_supported_variables(data)
        data = replace_env_variables(data)
        return replace_input_variables(data)

    # recursion
    elif isinstance(data, list):
        return [resolve_variables_data(item) for item in data]
    else:
        return {k: resolve_variables_data(v) for k, v in data.items()}
