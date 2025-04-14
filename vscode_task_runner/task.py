from __future__ import annotations

import os
import shutil
from typing import Any, Dict, List, Optional, Tuple, Union

import dacite

import vscode_task_runner.constants
import vscode_task_runner.helpers
import vscode_task_runner.terminal_task_system
from vscode_task_runner.exceptions import (
    DirectoryNotFound,
    FileNotFound,
    InvalidValue,
    UnsupportedValue,
)
from vscode_task_runner.models import (
    CommandString,
    ShellConfiguration,
    ShellType,
    TaskType,
)


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
            vscode_task_runner.constants.OPTIONS_KEY in self.all_task_data
            and setting_key
            in self.all_task_data[vscode_task_runner.constants.OPTIONS_KEY]
        ):
            value = self.all_task_data[vscode_task_runner.constants.OPTIONS_KEY][
                setting_key
            ]

        # global os-specific setting
        if (
            vscode_task_runner.constants.PLATFORM_KEY in self.all_task_data
            and vscode_task_runner.constants.OPTIONS_KEY
            in self.all_task_data[vscode_task_runner.constants.PLATFORM_KEY]
            and setting_key
            in self.all_task_data[vscode_task_runner.constants.PLATFORM_KEY][
                vscode_task_runner.constants.OPTIONS_KEY
            ]
        ):
            value = self.all_task_data[vscode_task_runner.constants.PLATFORM_KEY][
                vscode_task_runner.constants.OPTIONS_KEY
            ][setting_key]

        # task setting
        if (
            vscode_task_runner.constants.OPTIONS_KEY in self.task_data
            and setting_key in self.task_data[vscode_task_runner.constants.OPTIONS_KEY]
        ):
            value = self.task_data[vscode_task_runner.constants.OPTIONS_KEY][
                setting_key
            ]

        # task os-specific setting
        if (
            vscode_task_runner.constants.PLATFORM_KEY in self.task_data
            and vscode_task_runner.constants.OPTIONS_KEY
            in self.task_data[vscode_task_runner.constants.PLATFORM_KEY]
            and setting_key
            in self.task_data[vscode_task_runner.constants.PLATFORM_KEY][
                vscode_task_runner.constants.OPTIONS_KEY
            ]
        ):
            value = self.task_data[vscode_task_runner.constants.PLATFORM_KEY][
                vscode_task_runner.constants.OPTIONS_KEY
            ][setting_key]

        return value

    def _get_global_setting(self, setting_key: str, default: Any = None) -> Any:
        """
        Get a the value of a setting that is global.
        """
        return self.all_task_data.get(setting_key, default)

    def _get_task_setting(self, setting_key: str, default: Any = None) -> Any:
        """
        Get a the value of a setting that is specific to a task (like the command).
        Returns None if no value was found.
        """
        value = default

        # task setting
        if setting_key in self.task_data:
            value = self.task_data[setting_key]

        # task os-specific setting
        if (
            vscode_task_runner.constants.PLATFORM_KEY in self.task_data
            and setting_key in self.task_data[vscode_task_runner.constants.PLATFORM_KEY]
        ):
            value = self.task_data[vscode_task_runner.constants.PLATFORM_KEY][
                setting_key
            ]

        return value

    @property
    def is_virtual(self) -> bool:
        """
        Determines if the task is virtual (by not actually having any commands to run)
        """
        return not bool(self.command)

    @property
    def is_invalid(self) -> bool:
        """
        Determines if the task is not something we support.
        """
        try:
            # check if the task is valid
            self.type_
        except UnsupportedValue:
            return True

        if self.is_virtual and not self.depends_on:
            # check if the task is virtual and has no depends on
            return True

        return False

    @property
    def is_default_build_task(self) -> bool:
        """
        Determines if this task is the default build task
        """
        # https://stackoverflow.com/a/68028537/9944427
        if isinstance(self.task_data.get("group"), dict):
            return (
                self.task_data["group"].get("isDefault", False)
                and self.task_data["group"].get("kind", False) == "build"
            )

        return False

    @property
    def cwd(self) -> str:
        """
        Gets the current working directory of the task.
        """
        task_cwd = self._get_options_setting("cwd") or os.getcwd()

        # make sure the working directory exists
        if not os.path.isdir(task_cwd):
            raise DirectoryNotFound(f"Working directory '{task_cwd}' does not exist")

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
            env[key] = vscode_task_runner.helpers.stringify(value)

        return env

    @property
    def type_(self) -> TaskType:
        """
        Gets the type of the task.
        """
        task_type = self._get_task_setting(
            "type", vscode_task_runner.constants.DEFAULT_TASK_TYPE.value
        )

        # make sure an option was selected and is valid
        try:
            # only valid syntax in 3.12+
            # if task_type not in TaskType:
            return TaskType[task_type]
        except KeyError:
            raise UnsupportedValue(f"Unsupported task type '{task_type}'")

    @property
    def _global_command(self) -> Union[CommandString, None]:
        """
        Gets the globally configured command.
        """
        raw_global_command = self._get_global_setting("command")

        if raw_global_command is not None:
            return vscode_task_runner.helpers.load_command_string(raw_global_command)

    @property
    def _task_command(self) -> Union[CommandString, None]:
        """
        Gets the task command.
        """
        raw_task_command = self._get_task_setting("command")

        if raw_task_command is not None:
            return vscode_task_runner.helpers.load_command_string(raw_task_command)

    @property
    def command(self) -> Union[CommandString, None]:
        """
        Gets the final command to run for the task.
        """
        return self._task_command or self._global_command

    @property
    def args(self) -> List[CommandString]:
        """
        Get the arguments for the task.
        """
        global_args: List[str] = self._get_global_setting("args", default=[])
        task_args: List[str] = self._get_task_setting("args", default=[])

        # make sure it's a list
        if not isinstance(task_args, list) or not isinstance(global_args, list):
            raise InvalidValue("Invalid args format")

        # in the case that the command defined globally and in the task are the same,
        # tack on additional args
        if self.command == self._global_command:
            args_to_parse = global_args + task_args
        else:
            args_to_parse = task_args

        # parse all of the args
        final_args: List[CommandString] = []
        final_args.extend(
            vscode_task_runner.helpers.load_command_string(arg) for arg in args_to_parse
        )
        return final_args

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
            shell_configuration = vscode_task_runner.helpers.get_parent_shell()

        else:
            # make the shell executable absolute
            shell_configuration.executable = shutil.which(
                shell_configuration.executable
            )

        assert shell_configuration.executable is not None
        return shell_configuration, vscode_task_runner.helpers.identify_shell_type(
            shell_configuration.executable
        )

    def subprocess_command(self, extra_args: Optional[List[str]] = None) -> List[str]:
        """
        Generate the list of strings to pass to subprocess.
        """
        if extra_args is None:
            extra_args = []

        if self.type_ == TaskType.process:
            assert isinstance(self.command, str)
            which_task_command = shutil.which(self.command)

            if not which_task_command:
                # testing this line is impossible since other components
                # require patching shutil.which
                raise FileNotFound(
                    f"Unable to locate {self.command} in PATH"
                )  # pragma: no cover

            subprocess_command = [which_task_command]
            for arg in self.args + extra_args:
                # the args must be strings too
                assert isinstance(arg, str)
                subprocess_command.append(arg)

            return subprocess_command

        elif self.type_ == TaskType.shell:
            # first, get the shell information
            shell_config, shell_type = self.shell
            assert shell_config.executable is not None

            if shell_config.args is None:
                shell_config.args = []

            # build the shell quoting options
            vscode_task_runner.terminal_task_system.get_quoting_options(
                shell_type, shell_config
            )
            assert shell_config.quoting is not None

            # figure out how to tack on extra args
            command = self.command
            assert command is not None
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
            ] + vscode_task_runner.terminal_task_system.create_shell_launch_config(
                shell_type,
                shell_config.args,
                vscode_task_runner.terminal_task_system.build_shell_command_line(
                    shell_type,
                    shell_config.quoting,
                    command,
                    args,
                ),
            )

        else:
            # exception will be raied before here
            raise UnsupportedValue(
                f"Unsupported task type {self.type_}"
            )  # pragma: no cover

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
