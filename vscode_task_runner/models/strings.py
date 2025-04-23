from typing import Union

from pydantic import BaseModel

from vscode_task_runner.models.enums import ShellQuotingEnum
from vscode_task_runner.utils.strings import joiner
from vscode_task_runner.variables.resolve import resolve_variables_data


class QuotedStringConfig(BaseModel):
    """
    Dataclass for complex arguments. Used for configuration.
    """

    # https://github.com/microsoft/vscode/blob/e0c332665ce059efebb4477a90dd62e3aadcd688/src/vs/workbench/contrib/tasks/common/taskConfiguration.ts#L227-L228

    value: Union[str, list[str]]
    quoting: ShellQuotingEnum

    def resolve_variables(self) -> None:
        """
        Resolve variables for this quoted string.
        """
        self.value = resolve_variables_data(self.value)


CommandStringConfig = Union[QuotedStringConfig, list[str], str]
"""
Type alias for command strings. Used for configuration.
"""
# https://github.com/microsoft/vscode/blob/e0c332665ce059efebb4477a90dd62e3aadcd688/src/vs/workbench/contrib/tasks/common/taskConfiguration.ts#L227-L243


def csc_value(value: CommandStringConfig) -> str:
    if isinstance(value, str):
        return value
    elif isinstance(value, list):
        return joiner(value)
    elif isinstance(value.value, str):
        return value.value
    return joiner(value.value)


class QuotedString(BaseModel):
    """
    Dataclass for complex arguments. Used for runtime.
    """

    # https://github.com/microsoft/vscode/blob/eef30e7165e19b33daa1e15e92fa34ff4a5df0d3/src/vs/workbench/contrib/tasks/common/tasks.ts#L315-L318

    value: str
    quoting: ShellQuotingEnum


CommandString = Union[QuotedString, str]
"""
Type alias for command strings. Used for runtime.
"""
#  https://github.com/microsoft/vscode/blob/5944e7c37c6abb80f1cc822a8c5b593ef028ff26/src/vs/workbench/contrib/tasks/common/tasks.ts#L322-L332


def cs_value(value: CommandString) -> str:
    return value if isinstance(value, str) else value.value
