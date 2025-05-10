from typing import Dict, Optional

from pydantic import BaseModel, field_validator

from vscode_task_runner.models.shell import ShellConfiguration
from vscode_task_runner.variables.resolve import resolve_variables_data


class CommandOptions(BaseModel):
    """
    Regular options
    """

    # https://github.com/microsoft/vscode/blob/eef30e7165e19b33daa1e15e92fa34ff4a5df0d3/src/vs/workbench/contrib/tasks/common/tasks.ts#L102-L120

    shell: Optional[ShellConfiguration] = None
    """
    The shell to use if the task is a shell command.
    """
    cwd: Optional[str] = None
    """
    The current working directory of the executed program or shell.
    If omitted, the current working directory is used.
    Uses a string instead of DirectoryPath to allow for paths that may not exist
    on certain platforms.
    """
    env: Dict[str, str] = {}
    """
    The environment of the executed program or shell.
    If omitted, the parent process' environment is used.
    """

    @field_validator("env", mode="before")
    def stringify_env(cls, value: Dict[str, str]) -> Dict[str, str]:
        """
        Convert all values in the env dictionary to strings.
        Vscode tends to be pretty lax about only allowing strings,
        so replicate that behavior. `null` is not allowed.
        """
        response = {}
        for k, v in value.items():
            if v is None:
                raise ValueError(f"Environment variable {k} cannot be null")

            # convert booleans to strings in the same way as JS
            response[k] = str(v).lower() if isinstance(v, bool) else str(v)

        return response

    def resolve_variables(self) -> None:
        """
        Resolve variables for these command options.
        """

        if self.shell:
            self.shell.resolve_variables()

        self.cwd = resolve_variables_data(self.cwd)
        self.env = resolve_variables_data(self.env)
