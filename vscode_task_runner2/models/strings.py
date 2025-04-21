from typing import Union

from pydantic import BaseModel, RootModel

from vscode_task_runner2.models.enums import ShellQuoting


class QuotedString(BaseModel):
    """
    Dataclass for complex arguments
    """

    # https://github.com/microsoft/vscode/blob/eef30e7165e19b33daa1e15e92fa34ff4a5df0d3/src/vs/workbench/contrib/tasks/common/tasks.ts#L315-L318
    # https://github.com/microsoft/vscode/blob/e0c332665ce059efebb4477a90dd62e3aadcd688/src/vs/workbench/contrib/tasks/common/taskConfiguration.ts#L227-L228

    value: Union[str, list[str]]
    quoting: ShellQuoting


class CommandString(RootModel):
    # https://github.com/microsoft/vscode/blob/e0c332665ce059efebb4477a90dd62e3aadcd688/src/vs/workbench/contrib/tasks/common/taskConfiguration.ts#L227-L243
    root: Union[QuotedString, list[str], str]

    @property
    def value(self) -> str:
        if isinstance(self.root, str):
            return self.root
        elif isinstance(self.root, list):
            return " ".join(self.root)
        elif isinstance(self.root, QuotedString) and isinstance(self.root.value, str):
            return self.root.value

        return " ".join(self.root.value)
