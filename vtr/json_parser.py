import os
import re
from typing import Any, Tuple

import pyjson5

import vtr.constants


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


def replace_variables_data(data: Any) -> Any:
    """
    Recursively replaces variables in dictionary or list data.

    Parameters:
        data (Any): The data to recursively substitute.

    Returns:
        Any: A new dictionary or list with all variables processed.
    """
    if isinstance(data, dict):
        return {k: replace_variables_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [replace_variables_data(item) for item in data]
    elif isinstance(data, str):
        for key, value in vtr.constants.PREDEFINED_VARIABLES.items():
            data = data.replace(key, value)
        return replace_env_vars(data)
    else:
        return data


def load_vscode_tasks_data(path: str = os.getcwd()) -> Tuple[dict, str]:
    """
    Given a working directory, loads the vscode tasks config, and replaces
    all the variables. Returns raw dict data and the filename that was loaded.
    """
    tasks_json = os.path.join(path, ".vscode", "tasks.json")

    if not os.path.isfile(tasks_json):
        raise FileNotFoundError

    with open(tasks_json) as fp:
        tasks_json_data = pyjson5.load(fp)

    return replace_variables_data(tasks_json_data), tasks_json
