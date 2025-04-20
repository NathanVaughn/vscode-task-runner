class UnsupportedInput(Exception):
    """
    Exception raised when an input is an unsupported type (command)
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
