import os
from contextlib import contextmanager

IS_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"


def print_flush(msg: str) -> None:
    """
    Prints a message, but flushes the output for CI/CD.
    """
    print(msg, flush=True)


def info(msg: str) -> None:
    """
    Prints a standard message.
    """
    print_flush(msg)


def error(msg: str) -> None:
    """
    Prints an error to the console.
    """
    if IS_GITHUB_ACTIONS:
        print_flush(f"::error::{msg}")
    else:
        print_flush(msg)


def start_group(name: str) -> None:
    """
    Creates a new group in the GitHub Actions output.
    """
    if IS_GITHUB_ACTIONS:
        print_flush(f"::group::{name}")
    else:
        print_flush(f"Group: {name}")


def end_group() -> None:
    """
    Ends a group in the GitHub Actions output.
    """
    if IS_GITHUB_ACTIONS:
        print_flush("::endgroup::")


@contextmanager
def group(name: str):
    """
    Context manager for creating a group in the GitHub Actions output.
    """
    start_group(name)
    try:
        yield
    finally:
        end_group()
