import os

import questionary

from vscode_task_runner2.exceptions import ResponseNotProvided, UnsupportedInput
from vscode_task_runner2.models.inputs import Input, InputType


def get_input_value(input_: Input) -> str:
    """
    Given an input ID, prompt the user for the input value and return it.
    """
    # allow the user to provide the input value via environment variable
    if env_value := os.environ.get(f"VTR_INPUT_{input_.id}"):
        return env_value

    # otherwise, obtain from user input
    if input_.type_ == InputType.promptString:
        asker_type = questionary.text

        if input_.password is True:
            asker_type = questionary.password

        asker = asker_type(input_.description, default=input_.default)

    elif input_.type_ == InputType.pickString:
        # if the value should be picked from options
        asker = questionary.select(
            input_.description,
            choices=input_.options,
            default=input_.default,
        )

    else:
        raise UnsupportedInput(f"Unsupported input variable type '{input_.type_}'")

    output = asker.ask()
    if output is None:
        raise ResponseNotProvided("No response provided")  # pragma: no cover

    return output
