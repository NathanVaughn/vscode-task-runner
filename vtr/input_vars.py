from typing import List

import questionary


def get_input_value(input_id: str, inputs_data: List[dict]) -> str:
    """
    Given an input ID, prompt the user for the input value and return it.
    """
    input_data = next(i for i in inputs_data if i["id"] == input_id)

    if input_data["type"] == "promptString":
        if input_data.get("password", False) is True:
            # if the value is a password
            return questionary.password(
                input_data["description"], default=input_data.get("default", "")
            ).ask()

        # if the value is regular text
        return questionary.text(
            input_data["description"], default=input_data.get("default", "")
        ).ask()

    elif input_data["type"] == "pickString":
        # if the value should bed picked
        return questionary.select(
            input_data["description"],
            choices=input_data["options"],
            default=input_data.get("default"),
        ).ask()
    else:
        raise ValueError(f"Invalid input type '{input_data['type']}'")
