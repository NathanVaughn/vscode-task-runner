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

    # allow the user to provide the input value via environment variable
    if env_value := os.environ.get(f"VTR_INPUT_{input_id}"):
        return env_value

    # otherwise, obtain from user input
    if input_data["type"] == "promptString":
        if input_data.get("password", False) is True:
            # if the value is a password
            output = questionary.password(
                input_data["description"], default=input_data.get("default", "")
            ).ask()

        else:
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
        raise ResponseNotProvided("No response provided")  # pragma: no cover

    return output


def get_input_variables_values(
    commands: List[List[str]], inputs_data: Optional[List[dict]] = None
) -> Dict[str, str]:
    """
    Looks at the list of commands and finds all input variables and their values.
    This is done seperately, so as to not prompt for inputs for tasks that are not
    going to be run.
    """

    # https://code.visualstudio.com/docs/editor/variables-reference#_input-variables

    if inputs_data is None:
        inputs_data = []

    input_var_names = set()
    pattern = r"\${input:(.+?)}"

    for command in commands:
        for part in command:
            matches = re.findall(pattern, part)
            for match in matches:
                # make a set of all variables we need to get values for
                input_var_names.add(match)

    return {
        input_var_name: get_input_value(input_var_name, inputs_data)
        for input_var_name in input_var_names
    }


def replace_env_variables(string: str) -> str:
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


def replace_static_variables(data: Any, valid_parent: bool = False) -> Any:
    """
    Recursively replaces variables in dictionary or list data.
    Only replaces items under keys called "command", "args", or "options".
    """
    if isinstance(data, dict):
        return {
            k: replace_static_variables(v, valid_parent=True)
            if k in ("command", "args", "options")
            else replace_static_variables(v, valid_parent)
            for k, v in data.items()
        }
    elif isinstance(data, list):
        return [replace_static_variables(item, valid_parent) for item in data]
    elif isinstance(data, str) and valid_parent:
        # don't replace text if the parent keys are not in the list
        for key, value in SUPPORTED_PREDEFINED_VARIABLES.items():
            data = data.replace(key, value)

        for item in UNSUPPORTED_PREDEFINED_VARIABLES:
            if item in data:
                raise UnsupportedVariable(f"Unsupported variable '{item}'")

        return replace_env_variables(data)
    else:
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
