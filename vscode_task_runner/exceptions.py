class UnsupportedInput(Exception):
    """
    Exception raised when an input is an unsupported type (command)
    """


class UnsupportedVariable(Exception):
    """
    Exception raised when a referenced variable is unsupported
    """


class UnsupportedTaskType(Exception):
    """
    Raised when a task type is not supported
    """


class ResponseNotProvided(Exception):
    """
    When an input is cancelled by the user.
    """


class TasksFileNotFound(Exception):
    """
    .vscode/taks.json does not exist.
    """


class TasksFileInvalid(Exception):
    """
    .vscode/tasks.json is invalid.
    """


class ShellNotFound(Exception):
    """
    When a usable shell could not be identified
    """


class ExecutableNotFound(Exception):
    """
    When a binary file could not be found
    """


class MissingCommand(Exception):
    """
    When a task does not have a command defined but should (process)
    """


class WorkingDirectoryNotFound(Exception):
    """
    Raised when a defined working directory does not exist
    """


class BadInputEnvironmentVariable(Exception):
    """
    Raised when a task input provided by an environment variable is not one
    of the selections.
    """
