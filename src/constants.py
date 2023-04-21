import os
import platform

PLATFORM_KEYS = {
    "Windows": "windows",
    "Linux": "linux",
    "Darwin": "osx",
}

PLATFORM_KEY = PLATFORM_KEYS[platform.system()]

PREDEFINED_VARIABLES = {
    "${userHome}": os.path.expanduser("~"),
    "${workspaceFolder}": os.getcwd(),
    "${workspaceFolderBasename}": os.path.basename(os.getcwd()),
    "${pathSeparator}": os.path.sep,
}

OPTIONS_KEY = "options"
