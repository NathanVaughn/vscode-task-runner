import os
from contextlib import contextmanager
from typing import Generator

import colorama

IS_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"


def _print_flush(msg: str) -> None:
    """
    Prints a message, but flushes the output for CI/CD.
    """
    print(msg, flush=True)


def _color_string(msg: str, color: str) -> str:
    """
    Returns a colored string. Respects existing colors.
    """
    msg = msg.replace(colorama.Style.RESET_ALL, colorama.Style.RESET_ALL + color)
    return color + msg + colorama.Style.RESET_ALL


def info(msg: str) -> None:
    """
    Prints a standard message.
    """
    _print_flush(msg)


def error(msg: str) -> None:
    """
    Prints an error to the console.
    """
    if IS_GITHUB_ACTIONS:
        _print_flush(f"::error::{msg}")
    else:
        _print_flush(f"{red(msg)}")


def blue(msg: str) -> str:
    """
    Returns a blue-colored string. Respects existing colors.
    """
    return _color_string(msg, colorama.Fore.BLUE)


def yellow(msg: str) -> str:
    """
    Returns a yellow-colored string. Respects existing colors.
    """
    return _color_string(msg, colorama.Fore.YELLOW)


def red(msg: str) -> str:
    """
    Returns a red-colored string. Respects existing colors.
    """
    return _color_string(msg, colorama.Fore.RED)


def start_group(name: str) -> None:
    """
    Creates a new group in the GitHub Actions output.
    """
    if IS_GITHUB_ACTIONS:
        _print_flush(f"::group::{name}")


def end_group() -> None:
    """
    Ends a group in the GitHub Actions output.
    """
    if IS_GITHUB_ACTIONS:
        _print_flush("::endgroup::")


@contextmanager
def group(name: str) -> Generator[None, None, None]:
    """
    Context manager for creating a group in the GitHub Actions output.
    Does nothing outside GitHub Actions.
    """
    start_group(name)
    try:
        yield
    finally:
        end_group()
