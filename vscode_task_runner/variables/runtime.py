from vscode_task_runner.models.input import Input

# these variables will be filled out by the parser

RUNTIME_VARIABLES: dict[str, str] = {}
"""
Variables that can only be determined at runtime like defaultBuildTask.
Key is variable string, value is value.
"""
INPUTS: dict[str, Input] = {}
"""
User defined inputs.
Key is input id, value is Input object.
"""
