import os
import re
from functools import cache
from typing import Union, overload

import questionary

from vscode_task_runner2.exceptions import (
    ResponseNotProvided,
    UnsupportedInput,
    UnsupportedVariable,
)
from vscode_task_runner2.models.input import InputChoice, InputTypeEnum
from vscode_task_runner2.parser import INPUTS, RUNTIME_VARIABLES

# https://code.visualstudio.com/docs/editor/variables-reference#_predefined-variables
SUPPORTED_PREDEFINED_VARIABLES = {
    "${userHome}": os.path.expanduser("~"),
    "${workspaceFolder}": os.getcwd(),
    "${workspaceRoot}": os.getcwd(),
    "${workspaceFolderBasename}": os.path.basename(os.getcwd()),
    "${pathSeparator}": os.path.sep,
    "${/}": os.path.sep,
    "${cwd}": os.getcwd(),
}

UNSUPPORTED_PREDEFINED_VARIABLES = {
    "${file}",
    "${fileWorkspaceFolder}",
    "${relativeFile}",
    "${relativeFileDirname}",
    "${fileBasename}",
    "${fileBasenameNoExtension}",
    "${fileDirname}",
    "${fileDirnameBasename}",
    "${fileExtname}",
    "${lineNumber}",
    "${selectedText}",
    "${execPath}",
    "${extensionInstallFolder}",
}


@cache
def get_input_value(input_id: str) -> str:
    """
    Given an input ID, prompt the user for the input value and return it.
    """
    input_ = INPUTS[input_id]

    # allow the user to provide the input value via environment variable
    if env_value := os.environ.get(f"VTR_INPUT_{input_.id}"):
        return env_value

    # otherwise, obtain from user input
    if input_.type_ == InputTypeEnum.promptString:
        asker_type = questionary.text

        if input_.password is True:
            asker_type = questionary.password

        asker = asker_type(input_.description, default=input_.default)

    elif input_.type_ == InputTypeEnum.pickString:
        # if the value should be picked from options
        choices: list[Union[str, questionary.Choice]] = []

        # if the options are strings, add them as is
        # otherwise, add them as questionary.Choice
        for option in input_.options:
            if isinstance(option, InputChoice):
                choices.append(
                    questionary.Choice(title=option.label, value=option.value)
                )
            else:
                choices.append(option)

        asker = questionary.select(
            input_.description,
            choices=choices,
            default=input_.default,
        )

    else:
        raise UnsupportedInput(f"Unsupported input variable type '{input_.type_}'")

    output = asker.ask()
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
        data = data.replace(f"${{input:{match}}}", os.environ[match])

    return data


def replace_env_variables(data: str) -> str:
    """
    Replaces references to environment variables in a string with their values.
    """
    pattern = "\\${env:(.+?)}"
    matches = re.findall(pattern, data)
    for match in matches:
        data = data.replace(f"${{env:{match}}}", get_input_value(input_id=match))

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
    if data is None:
        return None

    if isinstance(data, str):
        # main data replacements
        check_unsupported_vars(data)
        check_unsupported_prefixes(data)

        data = replace_supported_variables(data)
        data = replace_env_variables(data)
        return replace_input_variables(data)

    # recursion
    elif isinstance(data, list):
        return [resolve_variables_data(item) for item in data]
    else:
        return {k: resolve_variables_data(v) for k, v in data.items()}
