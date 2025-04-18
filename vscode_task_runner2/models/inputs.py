import enum
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict


class InputType(str, enum.Enum):
    """Enum for input types."""

    promptString = "promptString"
    pickString = "pickString"
    command = "command"


class Input(BaseModel):
    """Model for inputs in tasks.json."""

    model_config = ConfigDict(extra="allow")

    type: InputType
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
    default: Optional[str] = None
    """
    Default value of the input.
    """
    options: Optional[List[str]] = None
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
