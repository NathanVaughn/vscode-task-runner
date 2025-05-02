import os
from contextlib import contextmanager
from typing import Generator

import colorama

IS_GITHUB_ACTIONS = bool(os.getenv("GITHUB_ACTIONS"))
IS_AZURE_PIPELINES = bool(os.getenv("TF_BUILD"))


def _print_flush(msg: str) -> None:  # pragma: no cover
    """
    Prints a message, but flushes the output for CI/CD.
    """
    print(msg, flush=True)


def _color_string(msg: str, color: str) -> str:  # pragma: no cover
    """
    Returns a colored string. Respects existing colors.
    """
    msg = msg.replace(colorama.Style.RESET_ALL, colorama.Style.RESET_ALL + color)
    return color + msg + colorama.Style.RESET_ALL


def info(msg: str) -> None:  # pragma: no cover
    """
    Prints a standard message.
    """
    _print_flush(msg)


def error(msg: str) -> None:  # pragma: no cover
    """
    Prints an error to the console.
    """
    if IS_GITHUB_ACTIONS:
        _print_flush(f"::error::{msg}")
    elif IS_AZURE_PIPELINES:
        _print_flush(f"##vso[task.logissue type=error]{msg}")
    else:
        _print_flush(f"{red(msg)}")


def blue(msg: str) -> str:  # pragma: no cover
    """
    Returns a blue-colored string. Respects existing colors.
    """
    return _color_string(msg, colorama.Fore.BLUE)


def yellow(msg: str) -> str:  # pragma: no cover
    """
    Returns a yellow-colored string. Respects existing colors.
    """
    return _color_string(msg, colorama.Fore.YELLOW)


def red(msg: str) -> str:  # pragma: no cover
    """
    Returns a red-colored string. Respects existing colors.
    """
    return _color_string(msg, colorama.Fore.RED)


def start_group(name: str) -> None:  # pragma: no cover
    """
    Creates a new group in the GitHub Actions output.
    """
    if IS_GITHUB_ACTIONS:
        _print_flush(f"::group::{name}")
    elif IS_AZURE_PIPELINES:
        _print_flush(f"##[group]{name}")


def end_group() -> None:  # pragma: no cover
    """
    Ends a group in the GitHub Actions output.
    """
    if IS_GITHUB_ACTIONS:
        _print_flush("::endgroup::")
    elif IS_AZURE_PIPELINES:
        _print_flush("##[endgroup]")


@contextmanager
def group(name: str) -> Generator[None, None, None]:  # pragma: no cover
    """
    Context manager for creating a group in the GitHub Actions output.
    Does nothing outside GitHub Actions.
    """
    start_group(name)
    try:
        yield
    finally:
        end_group()
