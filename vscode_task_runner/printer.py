import os
import sys
import threading
from contextlib import contextmanager
from typing import Generator, TextIO

import colorama

IS_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"
IS_AZURE_PIPELINES = os.getenv("TF_BUILD") == "true"

# Colors for different tasks (cycling through these)
TASK_COLORS = [
    colorama.Fore.CYAN,
    colorama.Fore.GREEN,
    colorama.Fore.MAGENTA,
    colorama.Fore.BLUE,
    colorama.Fore.YELLOW,
]

# Thread-local storage for task information
_thread_local = threading.local()


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
    elif IS_AZURE_PIPELINES:
        _print_flush(f"##vso[task.logissue type=error]{msg}")
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
    elif IS_AZURE_PIPELINES:
        _print_flush(f"##[group]{name}")


def end_group() -> None:
    """
    Ends a group in the GitHub Actions output.
    """
    if IS_GITHUB_ACTIONS:
        _print_flush("::endgroup::")
    elif IS_AZURE_PIPELINES:
        _print_flush("##[endgroup]")


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


class TaskOutputWrapper:
    """
    Wrapper for stdout/stderr that prefixes output with the task label.
    Used for parallel task execution to make it clear which output belongs to which task.
    """

    def __init__(self, stream: TextIO, task_label: str, color: str):
        self.stream = stream
        self.task_label = task_label
        self.color = color
        self.buffer = ""  # Buffer for incomplete lines

    def write(self, data: str) -> int:
        """Write data to the stream with task label prefix."""
        if not data:
            return 0

        # Add to buffer and process lines
        self.buffer += data

        # If we have a complete line (or multiple), process them
        if "\n" in self.buffer:
            lines = self.buffer.split("\n")
            # All but the last element are complete lines
            for line in lines[:-1]:
                # Don't prefix empty lines with task label
                if line:
                    prefix = (
                        f"{self.color}[{self.task_label}]{colorama.Style.RESET_ALL} "
                    )
                    self.stream.write(f"{prefix}{line}\n")
                else:
                    self.stream.write("\n")

            # The last element might be a partial line without a newline
            self.buffer = lines[-1]

        self.stream.flush()
        return len(data)

    def flush(self) -> None:
        """Flush any remaining buffer and the underlying stream."""
        if self.buffer:
            prefix = f"{self.color}[{self.task_label}]{colorama.Style.RESET_ALL} "
            self.stream.write(f"{prefix}{self.buffer}")
            self.buffer = ""
        self.stream.flush()

    def isatty(self) -> bool:
        """Pass through isatty to the underlying stream."""
        return self.stream.isatty()

    # Add other methods as needed to fully implement a file-like object
    def fileno(self) -> int:
        """Return the file descriptor of the underlying stream."""
        return self.stream.fileno()

    def close(self) -> None:
        """Close the wrapper but not the underlying stream."""
        self.flush()
        # Don't close the actual stdout/stderr


@contextmanager
def task_output_context(
    task_label: str, color_index: int = 0
) -> Generator[None, None, None]:
    """
    Context manager to set up task output wrapping.
    """
    # Choose a color based on the task (cycle through available colors)
    color = TASK_COLORS[color_index % len(TASK_COLORS)]

    # Save original stdout/stderr
    original_stdout = sys.stdout
    original_stderr = sys.stderr

    # Create wrappers
    wrapped_stdout = TaskOutputWrapper(original_stdout, task_label, color)
    wrapped_stderr = TaskOutputWrapper(original_stderr, task_label, color)

    # Replace stdout/stderr with wrapped versions
    sys.stdout = wrapped_stdout  # type: ignore
    sys.stderr = wrapped_stderr  # type: ignore

    try:
        yield
    finally:
        # Flush any remaining content
        wrapped_stdout.flush()
        wrapped_stderr.flush()

        # Restore original stdout/stderr
        sys.stdout = original_stdout
        sys.stderr = original_stderr
