from typing import Optional, overload

from vscode_task_runner2.models.strings import (
    CommandString,
    CommandStringConfig,
    QuotedString,
)


@overload
def shell_string(value: None) -> None: ...
@overload
def shell_string(value: str) -> str: ...
@overload
def shell_string(value: list[str]) -> str: ...
@overload
def shell_string(value: CommandStringConfig) -> CommandString: ...


def shell_string(value: Optional[CommandStringConfig]) -> Optional[CommandString]:
    # sourcery skip: assign-if-exp, reintroduce-else
    # https://github.com/microsoft/vscode/blob/52592e3ca8f6c18d612907245e809ddd24f76291/src/vs/workbench/contrib/tasks/common/taskConfiguration.ts#L943-L965
    if not value:
        return None

    if isinstance(value, str):
        return value
    elif isinstance(value, list):
        return " ".join(value)
    else:
        result = (
            value.value
            if isinstance(value.value, str)
            else " ".join(value.value)
            if isinstance(value.value, list)
            else None
        )
        if result:
            return QuotedString(value=result, quoting=value.quoting)

        return None
