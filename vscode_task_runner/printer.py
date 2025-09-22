import os
import sys
import tempfile
from contextlib import contextmanager
from typing import Generator, TextIO

import colorama

IS_GITHUB_ACTIONS = bool(os.getenv("GITHUB_ACTIONS"))
IS_AZURE_PIPELINES = bool(os.getenv("TF_BUILD"))


def _print_flush(msg: str, output: TextIO = sys.stdout) -> None:  # pragma: no cover
    """
    Prints a message, but flushes the output for CI/CD.
    """
    print(msg, flush=True, file=output)


def _color_string(msg: str, color: str) -> str:  # pragma: no cover
    """
    Returns a colored string. Respects existing colors.
    """
    msg = msg.replace(colorama.Style.RESET_ALL, colorama.Style.RESET_ALL + color)
    return color + msg + colorama.Style.RESET_ALL


def stdout(msg: str) -> None:  # pragma: no cover
    """
    Prints a message to standard output.
    """
    _print_flush(msg, output=sys.stdout)


def stderr(msg: str) -> None:  # pragma: no cover
    """
    Prints a message to standard output.
    """
    _print_flush(msg, output=sys.stderr)


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


def summary(
    completed_tasks: list[str], skipped_tasks: list[str], failed_tasks: list[str]
) -> None:  # pragma: no cover
    """
    Uploads a step summary in GitHub Actions/Azure Pipelines.
    """
    if os.environ.get("VTR_SKIP_SUMMARY"):
        return

    msg = ""

    # completed
    if completed_tasks:
        msg += f"## {len(completed_tasks)} Task{'s' * (len(completed_tasks) > 1)} Completed ✅\n\n"
        msg += "\n".join(f"- `{task}`" for task in completed_tasks) + "\n\n"

    # skipped
    if skipped_tasks:
        msg += f"## {len(skipped_tasks)} Task{'s' * (len(skipped_tasks) > 1)} Skipped ⏩\n\n"
        msg += "\n".join(f"- `{task}`" for task in skipped_tasks) + "\n\n"

    # failed
    if failed_tasks:
        msg += (
            f"## {len(failed_tasks)} Task{'s' * (len(failed_tasks) > 1)} Failed ❌\n\n"
        )
        msg += "\n".join(f"- `{task}`" for task in failed_tasks) + "\n\n"

    if IS_GITHUB_ACTIONS:
        summary_file = os.environ["GITHUB_STEP_SUMMARY"]
        with open(summary_file, "w", encoding="utf-8") as fp:
            fp.write(msg + "\n")

    elif IS_AZURE_PIPELINES:
        temp_file_fd, temp_file_name = tempfile.mkstemp(suffix=".md", text=True)
        with os.fdopen(temp_file_fd, "w", encoding="utf-8") as fp:
            fp.write(msg + "\n")

        _print_flush(f"##vso[task.uploadsummary]{temp_file_name}")


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
