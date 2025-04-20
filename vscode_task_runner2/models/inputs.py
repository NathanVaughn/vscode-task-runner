import enum
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class InputType(str, enum.Enum):
    """Enum for input types."""

    promptString = "promptString"
    pickString = "pickString"
    command = "command"


class Input(BaseModel):
    """Model for inputs in tasks.json."""

    model_config = ConfigDict(extra="allow")

    type_: InputType = Field(alias="type")
    """
    Type of the input
    """
    id: str
    """
    Id of the input
    """
    description: str
    """
    Description of the input.
    """
    default: str = ""
    """
    Default value of the input.
    """
    options: List[str] = Field(default_factory=list)
    """
    List of options for pickString input type.
    """
    password: Optional[bool] = None
    """
    Whether the input is a password or not for promptString input type.
    """
    command: Optional[str] = None
    """
    Command to execute for command input type.
    """
    args: Optional[Any] = None
    """
    Arguments to pass to the command for command input type.
    """
