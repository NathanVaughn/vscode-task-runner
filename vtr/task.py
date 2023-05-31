from __future__ import annotations

import os
import shutil
from typing import Any, Dict, List, Literal, Optional, Tuple

import dacite

import vtr.constants
import vtr.helpers
import vtr.terminal_task_system
from vtr.models import CommandString, ShellConfiguration, ShellType


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
            vtr.constants.OPTIONS_KEY in self.all_task_data
            and setting_key in self.all_task_data[vtr.constants.OPTIONS_KEY]
        ):
            value = self.all_task_data[vtr.constants.OPTIONS_KEY][setting_key]

        # global os-specific setting
        if (
            vtr.constants.PLATFORM_KEY in self.all_task_data
            and vtr.constants.OPTIONS_KEY
            in self.all_task_data[vtr.constants.PLATFORM_KEY]
            and setting_key
            in self.all_task_data[vtr.constants.PLATFORM_KEY][vtr.constants.OPTIONS_KEY]
        ):
            value = self.all_task_data[vtr.constants.PLATFORM_KEY][
                vtr.constants.OPTIONS_KEY
            ][setting_key]

        # task setting
        if (
            vtr.constants.OPTIONS_KEY in self.task_data
            and setting_key in self.task_data[vtr.constants.OPTIONS_KEY]
        ):
            value = self.task_data[vtr.constants.OPTIONS_KEY][setting_key]

        # task os-specific setting
        if (
            vtr.constants.PLATFORM_KEY in self.task_data
            and vtr.constants.OPTIONS_KEY in self.task_data[vtr.constants.PLATFORM_KEY]
            and setting_key
            in self.task_data[vtr.constants.PLATFORM_KEY][vtr.constants.OPTIONS_KEY]
        ):
            value = self.task_data[vtr.constants.PLATFORM_KEY][
                vtr.constants.OPTIONS_KEY
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
            vtr.constants.PLATFORM_KEY in self.task_data
            and setting_key in self.task_data[vtr.constants.PLATFORM_KEY]
        ):
            value = self.task_data[vtr.constants.PLATFORM_KEY][setting_key]

        return value

    @property
    def is_virtual(self) -> bool:
        """
        Determines if the task is virtual (by not actually having any commands to run)
        """
        return self._get_task_setting("command") is None

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
    def env(self) -> Dict[str, str]:
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
            env[key] = vtr.helpers.stringify(value)

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
        return vtr.helpers.load_command_string(raw_task_command)

    @property
    def args(self) -> List[CommandString]:
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
            task_args[i] = vtr.helpers.load_command_string(arg)

        return task_args

    @property
    def shell(self) -> Tuple[ShellConfiguration, ShellType]:
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
            shell_configuration = vtr.helpers.get_parent_shell()

        else:
            # make the shell executable absolute
            shell_configuration.executable = shutil.which(
                shell_configuration.executable
            )

        assert shell_configuration.executable is not None
        return shell_configuration, vtr.helpers.identify_shell_type(
            shell_configuration.executable
        )

    def subprocess_command(self, extra_args: Optional[List[str]] = None) -> List[str]:
        """
        Generate the list of strings to pass to subprocess.
        """
        if extra_args is None:
            extra_args = []

        if self.type_ == "process":
            assert isinstance(self.command, str)
            which_task_command = shutil.which(self.command)

            if not which_task_command:
                raise ValueError(f"Unable to locate {self.command} in PATH")

            subprocess_command = [which_task_command]
            for arg in self.args + extra_args:
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
            vtr.terminal_task_system.get_quoting_options(shell_type, shell_config)
            assert shell_config.quoting is not None

            # figure out how to tack on extra args
            command = self.command
            args = self.args

            if extra_args:
                # if we have args, tack it on to that
                if args:
                    args = args + extra_args
                else:
                    # if we only have a command, tack it on to that
                    extra_text = " " + " ".join(extra_args)

                    if isinstance(command, str):
                        command += extra_text
                    else:
                        command.value += extra_text

            return [
                shell_config.executable
            ] + vtr.terminal_task_system.create_shell_launch_config(
                shell_type,
                shell_config.args,
                vtr.terminal_task_system.build_shell_command_line(
                    shell_type,
                    shell_config.quoting,
                    command,
                    args,
                ),
            )

        else:
            raise ValueError("Unsupported task type")

    @property
    def depends_on(self) -> List[Task]:
        """
        Return a list of tasks this task depends on.
        """
        depends_on_setting = self._get_task_setting("dependsOn")

        # return empty list if not set
        if depends_on_setting is None:
            return []

        # a single string is allowed
        if isinstance(depends_on_setting, str):
            depends_on_setting = [depends_on_setting]

        # create task objects depending on the label
        return [Task(self.all_task_data, label) for label in depends_on_setting]
