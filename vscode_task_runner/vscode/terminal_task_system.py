"""
This file has functions from
vscode/src/vs/workbench/contrib/tasks/browser/terminalTaskSystem.ts
re-implemented in Python.
"""

import copy
import re
from typing import List, Optional, Tuple

from vscode_task_runner.constants import (
    DEFAULT_OS_QUOTING,
    DEFAULT_SHELL_QUOTING,
    PLATFORM_KEY,
)
from vscode_task_runner.models.enums import ShellQuotingEnum, ShellTypeEnum
from vscode_task_runner.models.shell import ShellConfiguration, ShellQuotingOptions
from vscode_task_runner.models.strings import CommandString
from vscode_task_runner.utils.strings import joiner


def get_quoting_options(shell_config: ShellConfiguration) -> ShellQuotingOptions:
    """
    Returns shell quoting options for given shell configuration
    """
    # https://github.com/microsoft/vscode/blob/5944e7c37c6abb80f1cc822a8c5b593ef028ff26/src/vs/workbench/contrib/tasks/browser/terminalTaskSystem.ts#L1606-L1611

    if shell_config.quoting:
        # return already defined options
        # there is no situation where this is already set
        # The user cannot specify this as an input
        # Appears to be dead code
        return shell_config.quoting  # pragma: no cover

    if shell_config.type_ in DEFAULT_SHELL_QUOTING:
        # otherwise return default for shell
        return DEFAULT_SHELL_QUOTING[shell_config.type_]

    # return default for OS if shell doesn't have defined options
    return DEFAULT_OS_QUOTING[PLATFORM_KEY]


def _add_all_argument(
    shell_command_args: List[str], configured_shell_args: List[str]
) -> List[str]:
    # https://github.com/microsoft/vscode/blob/5944e7c37c6abb80f1cc822a8c5b593ef028ff26/src/vs/workbench/contrib/tasks/browser/terminalTaskSystem.ts#L1306-L1321

    # converted with ChatGPT
    combined_shell_args = copy.deepcopy(configured_shell_args)
    for element in shell_command_args:
        should_add_shell_command_arg = all(
            (arg.lower() != element)
            # We can still add the argument, but only if not all of the following arguments begin with "-".
            or (
                (len(configured_shell_args) > index + 1)
                and (
                    not all(
                        test_arg.startswith("-")
                        for test_arg in configured_shell_args[index + 1 :]
                    )
                )
            )
            for index, arg in enumerate(configured_shell_args)
        )
        if should_add_shell_command_arg:
            combined_shell_args.append(element)

    return combined_shell_args


def create_shell_launch_config(
    shell_config: ShellConfiguration, command_line: str
) -> List[str]:
    """
    Should only be run if task is shell type
    """
    # https://github.com/microsoft/vscode/blob/eef30e7165e19b33daa1e15e92fa34ff4a5df0d3/src/vs/workbench/contrib/tasks/browser/terminalTaskSystem.ts#L1107-L1177

    # manually converted and simplified
    to_add: List[str] = []

    # skip all this if the user has already manually specific arguments
    if not shell_config.args:
        if shell_config.type_ == ShellTypeEnum.PowerShell:
            to_add.append("-Command")
        elif shell_config.type_ == ShellTypeEnum.SH:
            to_add.append("-c")
        elif shell_config.type_ == ShellTypeEnum.WSL:
            to_add.append("-e")
        elif shell_config.type_ == ShellTypeEnum.CMD:
            to_add.extend(["/d", "/c"])
        elif shell_config.type_ == ShellTypeEnum.Unknown:
            # default to a -c, works for most shells
            to_add.append("-c")

    combined_shell_args = _add_all_argument(to_add, shell_config.args)
    combined_shell_args.append(command_line)
    return combined_shell_args


def build_shell_command_line(
    shell_type: ShellTypeEnum,
    shell_quoting_options: ShellQuotingOptions,
    command: CommandString,
    args: List[CommandString],
) -> str:
    # Python re-implementation of
    # https://github.com/microsoft/vscode/blob/ab7c32a5b5275c3fa9552675b6b6035888068fd7/src/vs/workbench/contrib/tasks/browser/terminalTaskSystem.ts#L1476-L1573

    # Largely done by ChatGPT with some manual tweaks

    def needs_quotes(value: str) -> bool:
        # https://github.com/microsoft/vscode/blob/5944e7c37c6abb80f1cc822a8c5b593ef028ff26/src/vs/workbench/contrib/tasks/browser/terminalTaskSystem.ts#L1511-L1537
        if len(value) >= 2:
            first = (
                shell_quoting_options.strong
                if value[0] == shell_quoting_options.strong
                else shell_quoting_options.weak
                if value[0] == shell_quoting_options.weak
                else None
            )
            if first == value[-1]:
                return False

        quote: Optional[str] = None
        skip = False

        for ch in value:
            # allow us to skip loop iterations
            if skip:
                skip = False
                continue

            # We found the end quote.
            if ch == quote:
                quote = None
            elif quote is not None:
                # skip the character. We are quoted.
                continue
            elif ch == shell_quoting_options.escape:
                # Skip the next character
                skip = True
            elif ch in (shell_quoting_options.strong, shell_quoting_options.weak):
                quote = ch
            elif ch == " ":
                return True
        return False

    def quote(value: str, kind: ShellQuotingEnum) -> Tuple[str, bool]:
        # https://github.com/microsoft/vscode/blob/5944e7c37c6abb80f1cc822a8c5b593ef028ff26/src/vs/workbench/contrib/tasks/browser/terminalTaskSystem.ts#L1539-L1559
        if kind == ShellQuotingEnum.strong and shell_quoting_options.strong:
            return (
                shell_quoting_options.strong + value + shell_quoting_options.strong,
                True,
            )
        elif kind == ShellQuotingEnum.weak and shell_quoting_options.weak:
            return (
                shell_quoting_options.weak + value + shell_quoting_options.weak,
                True,
            )
        elif kind == ShellQuotingEnum.escape and shell_quoting_options.escape:
            if isinstance(shell_quoting_options.escape, str):
                return value.replace(" ", f"{shell_quoting_options.escape} "), True
            buffer = []
            for ch in shell_quoting_options.escape.characters_to_escape:
                buffer.append("\\" + ch)
            regexp = re.compile("[" + ",".join(buffer) + "]")
            escape_char = shell_quoting_options.escape.escape_character
            return (
                regexp.sub(lambda match: escape_char + match.group(), value),
                True,
            )
        return (value, False)

    def quote_if_necessary(value: CommandString) -> Tuple[str, bool]:
        # https://github.com/microsoft/vscode/blob/5944e7c37c6abb80f1cc822a8c5b593ef028ff26/src/vs/workbench/contrib/tasks/browser/terminalTaskSystem.ts#L1560-L1570
        if isinstance(value, str):
            if needs_quotes(value):
                # default of strong quoting
                return quote(value, ShellQuotingEnum.strong)
            else:
                return (value, False)
        else:
            return quote(value.value, value.quoting)

    # If we have no args and the command is a string then use the command to stay
    # backwards compatible with the old command line model. To allow variable resolving
    # with spaces we do continue if the resolved value is different than the original
    # one and the resolved one needs quoting.
    if not args and isinstance(command, str):
        return command

    result: List[str] = []
    command_quoted = False
    arg_quoted = False
    value, quoted = quote_if_necessary(command)
    result.append(value)
    command_quoted = quoted
    for arg in args:
        value, quoted = quote_if_necessary(arg)
        result.append(value)
        arg_quoted = arg_quoted or quoted

    command_line = joiner(result)
    # There are special rules quoted command line in cmd.exe
    if PLATFORM_KEY == "windows":
        if shell_type == ShellTypeEnum.CMD and command_quoted and arg_quoted:
            command_line = f'"{command_line}"'
        elif shell_type == ShellTypeEnum.PowerShell and command_quoted:
            command_line = f"& {command_line}"

    return command_line
