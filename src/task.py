import os
import shutil
from typing import Any, Literal

import dacite

import src.constants
import src.helpers
import src.terminal_task_system
from src.models import ShellConfiguration, ShellType
from src.typehints import CommandString


class Task:
    def __init__(self, all_task_data: dict, task_label: str) -> None:
        self.all_task_data = all_task_data
        self.label = task_label

        self.task_data = next(
            task for task in self.all_task_data["tasks"] if task["label"] == self.label
        )

    def _get_options_setting(self, setting_key: str) -> Any:
        """
        Get a the value of a setting that is nested under the "options" key.
        Returns None if no value was found.
        """
        value = None

        # global setting
        if (
            src.constants.OPTIONS_KEY in self.all_task_data
            and setting_key in self.all_task_data[src.constants.OPTIONS_KEY]
        ):
            value = self.all_task_data[src.constants.OPTIONS_KEY][setting_key]

        # global os-specific setting
        if (
            src.constants.PLATFORM_KEY in self.all_task_data
            and src.constants.OPTIONS_KEY
            in self.all_task_data[src.constants.PLATFORM_KEY]
            and setting_key
            in self.all_task_data[src.constants.PLATFORM_KEY][src.constants.OPTIONS_KEY]
        ):
            value = self.all_task_data[src.constants.PLATFORM_KEY][
                src.constants.OPTIONS_KEY
            ][setting_key]

        # task setting
        if (
            src.constants.OPTIONS_KEY in self.task_data
            and setting_key in self.task_data[src.constants.OPTIONS_KEY]
        ):
            value = self.task_data[src.constants.OPTIONS_KEY][setting_key]

        # task os-specific setting
        if (
            src.constants.PLATFORM_KEY in self.task_data
            and src.constants.OPTIONS_KEY in self.task_data[src.constants.PLATFORM_KEY]
            and setting_key
            in self.task_data[src.constants.PLATFORM_KEY][src.constants.OPTIONS_KEY]
        ):
            value = self.task_data[src.constants.PLATFORM_KEY][
                src.constants.OPTIONS_KEY
            ][setting_key]

        return value

    def _get_task_setting(self, setting_key: str) -> Any:
        """
        Get a the value of a setting that is specific to a task (like the command).
        Returns None if no value was found.
        """
        value = None

        # task setting
        if setting_key in self.task_data:
            value = self.task_data[setting_key]

        # task os-specific setting
        if (
            src.constants.PLATFORM_KEY in self.task_data
            and setting_key in self.task_data[src.constants.PLATFORM_KEY]
        ):
            value = self.task_data[src.constants.PLATFORM_KEY][setting_key]

        return value

    @property
    def cwd(self) -> str:
        """
        Gets the current working directory of the task.
        """
        task_cwd = self._get_options_setting("cwd") or os.getcwd()

        # make sure the working directory exists
        if not os.path.isdir(task_cwd):
            raise FileNotFoundError(f"Working directory '{task_cwd}' does not exist")

        return task_cwd

    @property
    def env(self) -> dict[str, str]:
        """
        Gets the environment variables for the task. This merges with the current
        environment variables.
        """
        # copy the current environment
        env = os.environ.copy()

        task_env = self._get_options_setting("env")
        if isinstance(task_env, dict):
            # merge environments
            env = {**env, **task_env}

        # convert everything to strings, and make sure it's simple key-value pairs
        for key, value in env.items():
            if not isinstance(key, str):
                raise EnvironmentError(f"Key {key} is not a string")

            env[key] = src.helpers.stringify(value)

        return env

    @property
    def type_(self) -> Literal["shell", "process"]:
        """
        Gets the type of the task.
        """
        task_type = self._get_task_setting("type")

        # apply default value
        if task_type is None:
            task_type = "process"

        # make sure an option was selected and is valid
        if task_type not in ("shell", "process"):
            raise ValueError(f"Invalid task type '{task_type}'")

        return task_type

    @property
    def command(self) -> CommandString:
        """
        Gets the command for the task.
        """
        raw_task_command = self._get_task_setting("command")
        return src.helpers.load_command_string(raw_task_command)

    @property
    def args(self) -> list[CommandString]:
        """
        Get the arguments for the task.
        """
        task_args = self._get_task_setting("args")

        # no args given
        if task_args is None:
            return []

        # make sure it's a list
        if not isinstance(task_args, list):
            raise ValueError("Invalid args format")

        for i, arg in enumerate(task_args):
            task_args[i] = src.helpers.load_command_string(arg)

        return task_args

    @property
    def shell(self) -> tuple[ShellConfiguration, ShellType]:
        """
        Gets the shell configuration the task is going to run under.
        """
        shell_dict = self._get_options_setting("shell")

        if shell_dict is not None:
            # if shell settings defined
            shell_configuration = dacite.from_dict(
                data_class=ShellConfiguration, data=shell_dict
            )
        else:
            # if not, create empty
            shell_configuration = ShellConfiguration()

        if not shell_configuration.executable:
            # if we still don't have a shell, use the parent shell
            shell_configuration = src.helpers.get_parent_shell()

        else:
            # make the shell executable absolute
            shell_configuration.executable = shutil.which(
                shell_configuration.executable
            )

        assert shell_configuration.executable is not None
        return shell_configuration, src.helpers.identify_shell_type(
            shell_configuration.executable
        )

    @property
    def subprocess_command(self) -> list[str]:
        if self.type_ == "process":
            assert isinstance(self.command, str)
            which_task_command = shutil.which(self.command)

            if not which_task_command:
                raise ValueError(f"Unable to locate {self.command} in PATH")

            subprocess_command = [which_task_command]
            if self.args is not None:
                for arg in self.args:
                    # the args must be strings too
                    assert isinstance(arg, str)
                    subprocess_command.append(arg)

            return subprocess_command

        elif self.type_ == "shell":
            # first, get the shell information
            shell_config, shell_type = self.shell
            assert shell_config.executable is not None

            if shell_config.args is None:
                shell_config.args = []

            # build the shell quoting options
            src.terminal_task_system.get_quoting_options(shell_type, shell_config)
            assert shell_config.quoting is not None

            return [
                shell_config.executable
            ] + src.terminal_task_system.create_shell_launch_config(
                shell_type,
                shell_config.args,
                src.terminal_task_system.build_shell_command_line(
                    shell_type, shell_config.quoting, self.command, self.args
                ),
            )

        else:
            raise ValueError("Unsupported task type")
