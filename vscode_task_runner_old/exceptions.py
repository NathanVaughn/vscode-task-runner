class TasksFileNotFound(Exception):
    """
    .vscode/taks.json does not exist.
    """

    pass


class FileNotFound(Exception):
    """
    When a file does not exist.
    """

    pass


class DirectoryNotFound(Exception):
    """
    When a directory like a task working directory does not exist.
    """

    pass


class ShellNotFound(Exception):
    """
    A shell could not be located.
    """

    pass


class UnsupportedVariable(Exception):
    """
    Used when a variable is present that is not supported.
    """

    pass


class UnsupportedValue(Exception):
    """
    Used when a selected value is valid but not supported.
    """

    pass


class InvalidValue(Exception):
    """
    Used when an item is invalid, not just unsupported. Like a string that should
    be a list.
    """

    pass


class ResponseNotProvided(Exception):
    """
    When an input is cancelled by the user.
    """

    pass
