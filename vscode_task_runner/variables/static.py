import os

# https://code.visualstudio.com/docs/editor/variables-reference#_predefined-variables
SUPPORTED_PREDEFINED_VARIABLES = {
    "${userHome}": os.path.expanduser("~"),
    "${workspaceFolder}": os.getcwd(),
    "${workspaceRoot}": os.getcwd(),
    "${workspaceFolderBasename}": os.path.basename(os.getcwd()),
    "${pathSeparator}": os.path.sep,
    "${/}": os.path.sep,
    "${cwd}": os.getcwd(),
}

UNSUPPORTED_PREDEFINED_VARIABLES = {
    "${file}",
    "${fileWorkspaceFolder}",
    "${relativeFile}",
    "${relativeFileDirname}",
    "${fileBasename}",
    "${fileBasenameNoExtension}",
    "${fileDirname}",
    "${fileDirnameBasename}",
    "${fileExtname}",
    "${lineNumber}",
    "${selectedText}",
    "${execPath}",
    "${extensionInstallFolder}",
}
