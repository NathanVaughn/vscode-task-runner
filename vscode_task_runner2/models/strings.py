from typing import Union

from pydantic import BaseModel, RootModel

from vscode_task_runner2.models.enums import ShellQuoting


class QuotedString(BaseModel):
    """
    Dataclass for complex arguments
    """

    # https://github.com/microsoft/vscode/blob/eef30e7165e19b33daa1e15e92fa34ff4a5df0d3/src/vs/workbench/contrib/tasks/common/tasks.ts#L315-L318

    value: Union[str, list[str]]
    quoting: ShellQuoting


CommandString = Union[QuotedString, str]
# https://github.com/microsoft/vscode/blob/eef30e7165e19b33daa1e15e92fa34ff4a5df0d3/src/vs/workbench/contrib/tasks/common/tasks.ts#L320


class StringListStringQuotedStringType(RootModel):
    root: Union[QuotedString, list[str], str]
    # ! Order is important for pydantic

    def export_command_string(self) -> CommandString:
        """
        Export the string data to a CommandString
        """
        if isinstance(self.root, str):
            return self.root
        elif isinstance(self.root, list):
            return " ".join(self.root)
        elif isinstance(self.root, QuotedString):
            return self.root
        else:
            raise ValueError(f"Invalid type {type(self.root)}")
