"""
This file has functions from
vscode/src/vs/workbench/contrib/tasks/browser/terminalTaskSystem.ts
re-implemented in Python.
"""

import copy
import re
from typing import List, Optional, Tuple, Union

import vtr.constants
from vtr.models import (
    CommandString,
    ShellConfiguration,
    ShellQuoting,
    ShellQuotingOptions,
    ShellType,
)


def get_quoting_options(
    shell_type: ShellType, shell_config: ShellConfiguration
) -> None:
    """
    Operates in-place on input ShellConfiguration to fill out quoting options
    """
    if shell_config.quoting:
        return

    if shell_type in vtr.constants.DEFAULT_SHELL_QUOTING:
        shell_config.quoting = vtr.constants.DEFAULT_SHELL_QUOTING[shell_type]
    else:
        shell_config.quoting = vtr.constants.DEFAULT_OS_QUOTING[
            vtr.constants.PLATFORM_KEY
        ]


def _add_all_argument(
    shell_command_args: List[str], configured_shell_args: List[str]
) -> List[str]:
    # https://github.com/microsoft/vscode/blob/eef30e7165e19b33daa1e15e92fa34ff4a5df0d3/src/vs/workbench/contrib/tasks/browser/terminalTaskSystem.ts#L1256-L1272

    # converted with ChatGPT
    combined_shell_args = copy.deepcopy(configured_shell_args)
    for element in shell_command_args:
        should_add_shell_command_arg = all(
            (arg.lower() != element)
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
    shell_type: ShellType, shell_args: Union[List[str], str], command_line: str
) -> List[str]:
    # https://github.com/microsoft/vscode/blob/eef30e7165e19b33daa1e15e92fa34ff4a5df0d3/src/vs/workbench/contrib/tasks/browser/terminalTaskSystem.ts#L1107-L1177

    # manually converted and simplified

    # convert a single shell args string into a list
    if isinstance(shell_args, str):
        shell_args = [shell_args]

    to_add: List[str] = []

    # skip all this if the user has already manually specific arguments
    if not shell_args:
        # this cannot happen in our case, since we don't have default
        # arguments loaded from settings.

        # Under Mac remove -l to not start it as a login shell.
        # if vtr.constants.PLATFORM_KEY == "osx" and "-l" in shell_args:
        #     shell_args.remove("-l")

        if shell_type == ShellType.PowerShell:
            to_add.append("-Command")
        elif shell_type == ShellType.SH:
            to_add.append("-c")
        elif shell_type == ShellType.WSL:
            to_add.append("-e")
        elif shell_type == ShellType.CMD:
            to_add.extend(["/d", "/c"])

    combined_shell_args = _add_all_argument(to_add, shell_args)
    combined_shell_args.append(command_line)

    # if windows_shell_args:
    #     return [" ".join(combined_shell_args)]
    # else:
    #     return combined_shell_args
    return combined_shell_args


def build_shell_command_line(
    shell_type: ShellType,
    shell_quoting_options: ShellQuotingOptions,
    task_command: CommandString,
    args: List[CommandString],
) -> str:
    # Python re-implementation of
    # https://github.com/microsoft/vscode/blob/ab7c32a5b5275c3fa9552675b6b6035888068fd7/src/vs/workbench/contrib/tasks/browser/terminalTaskSystem.ts#L1476-L1573

    # Largely done by ChatGPT with some manual tweaks

    def needs_quotes(value: str) -> bool:
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
            elif ch in [
                shell_quoting_options.strong,
                shell_quoting_options.weak,
            ]:
                quote = ch
            elif ch == " ":
                return True
        return False

    def quote(value: str, kind: ShellQuoting) -> Tuple[str, bool]:
        if kind == ShellQuoting.Strong and shell_quoting_options.strong:
            return (
                shell_quoting_options.strong + value + shell_quoting_options.strong,
                True,
            )
        elif kind == ShellQuoting.Weak and shell_quoting_options.weak:
            return (
                shell_quoting_options.weak + value + shell_quoting_options.weak,
                True,
            )
        elif kind == ShellQuoting.Escape and shell_quoting_options.escape:
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
        if isinstance(value, str):
            if needs_quotes(value):
                # default of strong quoting
                return quote(value, ShellQuoting.Strong)
            else:
                return (value, False)
        else:
            return quote(value.value, value.quoting)

    # If we have no args and the command is a string then use the command to stay
    # backwards compatible with the old command line model. To allow variable resolving
    # with spaces we do continue if the resolved value is different than the original
    # one and the resolved one needs quoting.
    if not args and isinstance(task_command, str):
        return task_command

    result: List[str] = []
    command_quoted = False
    arg_quoted = False
    value, quoted = quote_if_necessary(task_command)
    result.append(value)
    command_quoted = quoted
    for arg in args:
        value, quoted = quote_if_necessary(arg)
        result.append(value)
        arg_quoted = arg_quoted or quoted

    command_line = " ".join(result)
    # There are special rules quoted command line in cmd.exe
    if vtr.constants.PLATFORM_KEY == "windows":
        if shell_type == ShellType.CMD and command_quoted and arg_quoted:
            command_line = f'"{command_line}"'
        elif shell_type == ShellType.PowerShell and command_quoted:
            command_line = f"& {command_line}"

    return command_line
