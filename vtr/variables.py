import os
import re
from typing import Any, Dict, List, Optional

import questionary

from vtr.exceptions import ResponseNotProvided, UnsupportedValue, UnsupportedVariable

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
    "${fileExtname}",
    "${lineNumber}",
    "${selectedText}",
    "${execPath}",
}


def get_input_value(input_id: str, inputs_data: List[dict]) -> str:
    """
    Given an input ID, prompt the user for the input value and return it.
    """
    input_data = next(i for i in inputs_data if i["id"] == input_id)

    if input_data["type"] == "promptString":
        if input_data.get("password", False) is True:
            # if the value is a password
            output = questionary.password(
                input_data["description"], default=input_data.get("default", "")
            ).ask()

        # if the value is regular text
        output = questionary.text(
            input_data["description"], default=input_data.get("default", "")
        ).ask()

    elif input_data["type"] == "pickString":
        # if the value should be picked from options
        output = questionary.select(
            input_data["description"],
            choices=input_data["options"],
            default=input_data.get("default"),
        ).ask()
    else:
        raise UnsupportedValue(
            f"Unsupported input variable type '{input_data['type']}'"
        )

    if output is None:
        raise ResponseNotProvided("No response provided")

    return output


def get_input_vars_values(
    commands: List[List[str]], inputs_data: Optional[List[dict]] = None
) -> Dict[str, str]:
    """
    Looks at the list of commands and finds all input variables and their values.
    """
    if inputs_data is None:
        inputs_data = []

    input_vars = {}
    pattern = r"\${input:(.+?)}"

    for command in commands:
        for part in command:
            matches = re.findall(pattern, part)
            for match in matches:
                input_vars[match] = get_input_value(match, inputs_data)

    return input_vars


def replace_env_vars(string: str) -> str:
    """
    Replaces references to environment variables in a string with their values.

    Parameters:
        string (str): The string to replace environment variable references in.

    Returns:
        str: The modified string with all environment variable references replaced by their values.
    """
    pattern = r"\${env:(.+?)}"
    matches = re.findall(pattern, string)
    for match in matches:
        string = string.replace(f"${{env:{match}}}", os.environ[match])

    return string


def replace_recursive(data: Any) -> Any:
    """
    Recursively replaces variables in dictionary or list data.
    """
    if isinstance(data, dict):
        return {k: replace_recursive(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [replace_recursive(item) for item in data]
    elif isinstance(data, str):
        for key, value in SUPPORTED_PREDEFINED_VARIABLES.items():
            data = data.replace(key, value)

        for item in UNSUPPORTED_PREDEFINED_VARIABLES:
            if item in data:
                raise UnsupportedVariable(f"Unsupported variable '{item}'")

        return replace_env_vars(data)
    else:
        return data


def replace_static_variables(data: dict) -> dict:
    """
    Recursively replaces variables in dictionary or list data.
    Only replaces items under keys called "command", "args", or "options".
    """
    if not isinstance(data, dict):
        return data

    for k, v in data.items():
        if k in ("command", "args", "options"):
            data[k] = replace_recursive(v)

    return data


def replace_runtime_variables(
    data: List[str],
    input_vars_values: Dict[str, str],
    default_build_task: Optional[str] = None,
) -> List[str]:
    """
    Replaces variables in a list of strings.
    """
    output = []
    for string in data:
        for key, value in input_vars_values.items():
            string = string.replace(f"${{input:{key}}}", value)

        if default_build_task:
            string = string.replace("${defaultBuildTask}", default_build_task)

        output.append(string)

    return output
