from __future__ import annotations

from typing import List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, model_validator

from vscode_task_runner.models.enums import InputTypeEnum


class InputChoice(BaseModel):
    label: str
    value: str


class Input(BaseModel):
    """Model for inputs in tasks.json."""

    model_config = ConfigDict(extra="allow")

    type_: InputTypeEnum = Field(alias="type")
    """
    Type of the input
    """
    id: str
    """
    Id of the input
    """
    description: str = ""
    """
    Description of the input. Not allowed for command input type.
    """
    default: Optional[str] = None
    """
    Default value of the input.
    """
    options: List[Union[str, InputChoice]] = Field(default_factory=list)
    """
    List of options for pickString input type.
    """
    password: Optional[bool] = None
    """
    Whether the input is a password or not for promptString input type.
    """

    @model_validator(mode="after")
    def verify_options(self) -> Input:
        """
        Ensure the list of options is at least 1
        """
        if self.type_ == InputTypeEnum.pickString and not self.options:
            raise ValueError("pickString input must have at least one option")

        return self

    @model_validator(mode="after")
    def verify_default(self) -> Input:
        """
        Verify that the default value is in the options
        """
        if self.type_ != InputTypeEnum.pickString:
            # skip if not a pickString input
            return self

        if self.default is None:
            # if no default value is set, skip the check
            return self

        # convert options into a list of values
        option_values = []
        for option in self.options:
            if isinstance(option, InputChoice):
                option_values.append(option.value)
            else:
                option_values.append(option)

        if self.default not in option_values:
            raise ValueError(
                f"Default value '{self.default}' not in options: {option_values}"
            )

        return self
