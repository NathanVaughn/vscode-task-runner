import os
from typing import Any, Literal

# import like this so mocks work
import src.constants
import src.helpers


class Task:
    def __init__(self, all_task_data: dict, task_label: str) -> None:
        self.all_task_data = all_task_data
        self.task_label = task_label

        self.task_data = next(
            task
            for task in self.all_task_data["tasks"]
            if task["label"] == self.task_label
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
        task_cwd = self._get_options_setting("cwd") or os.getcwd()

        # make sure the working directory exists
        if not os.path.isdir(task_cwd):
            raise ValueError(f"Working directory '{task_cwd}' does not exist")

        return task_cwd

    @property
    def env(self) -> dict[str, str]:
        # copy the current environment
        env = os.environ.copy()

        if task_env := self._get_options_setting("env"):
            # merge environments
            env = {**env, **task_env}

        if not isinstance(task_env, dict):
            raise ValueError("Invalid environment format")

        # convert everything to strings, and make sure it's simple key-value pairs
        for key, value in env.items():
            if not isinstance(key, str):
                raise ValueError(f"Key {key} is not a string")

            env[key] = src.helpers.stringify(value)

        return env

    @property
    def type_(self) -> Literal["shell", "process"]:
        task_type = self._get_task_setting("type")

        # apply default value
        if task_type is None:
            task_type = "process"

        # make sure an option was selected and is valid
        if task_type not in ("shell", "process"):
            raise ValueError(f"Invalid task type '{task_type}'")

        return task_type

    @property
    def command(self) -> str:
        task_command = self._get_task_setting("command")

        # make sure the command is a string
        if not isinstance(task_command, str):
            raise ValueError(f"Command '{task_command}' is not valid")

        return task_command

    @property
    def args(self) -> list[str]:
        # needs to support quoting for args
        task_args = self._get_task_setting("args")

        if task_args is not None:
            # make sure it's a list
            if not isinstance(task_args, list):
                raise ValueError("Invalid args format")

            for i, arg in enumerate(task_args):
                task_args[i] = src.helpers.stringify(arg)

        return task_args
