# VS Code Task Runner

This is a command-line tool to execute VS Code
[Tasks](https://code.visualstudio.com/docs/editor/tasks)
defined in the `.vscode/tasks.json` file.
This allows you to write Tasks once, and run them in the same manner in your editor
and in CI/CD.

This tool aims to be as feature-complete as possible with what VS Code supports for
Windows, MacOSX and Linux. Much of the logic is taken directly from the VS Code
source code and reimplemented in Python.

This pairs well with VS Code extensions that add Task buttons such as
[actboy168.tasks](https://marketplace.visualstudio.com/items?itemName=actboy168.tasks).

## Usage

Python 3.10+ is required.

Install with pip/pipx:

```bash
pip install vscode-task-runner
```

Use the command `vtr` on the command line and provide the name of the Task(s).
There must be a `.vscode/tasks.json` file in the working directory you run the
command in.

## Examples

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Pre-Commit",
            "type": "shell",
            "command": "poetry run pre-commit run --all-files",
        }
    ]
}
```

```shell
$ vtr "Pre-Commit"
Executing: C:\Program Files\WindowsApps\Microsoft.PowerShell_7.3.4.0_x64__8wekyb3d8bbwe\pwsh.exe -Command poetry run pre-commit run --all-files
check json...............................................................Passed
check toml...............................................................Passed
check yaml...............................................................Passed
check for case conflicts.................................................Passed
trim trailing whitespace.................................................Passed
check for merge conflicts................................................Passed
mixed line ending........................................................Passed
poetry-check.............................................................Passed
poetry-lock..............................................................Passed
absolufy-imports.........................................................Passed
ruff.....................................................................Passed
black....................................................................Passed
pyleft...................................................................Passed
pyright..................................................................Passed
markdownlint.............................................................Passed
```

## Implemented Features

- Predefined variables:
  - `${userHome}`
  - `${workspaceFolder}`
  - `${workspaceFolderBasename}`
  - `${pathSeparator}`
  - `${cwd}`
  - `${env:VARIABLE}`
- Settings hierarchy:
  - Global level settings
  - Global level OS-specific settings
  - Task level settings
  - Task level OS-specific settings
- Task configuration:
  - `cwd`
  - `env`
  - `type`
    - `"process"`
    - `"shell"`
  - `command`
  - `args`
  - `shell`
- Quoting support:
  - `"escape"`
  - `"strong"`
  - `"weak"`

## Unsupported Features

- Any predefined variable not listed above. The other variables tend to rely
  upon a file open VS Code, or VS Code itself.
- Problem matchers
- Background tasks
- UNC path conversion
- Parallel `dependsOn` task execution
- Task types other than `"process"` or `"shell"`

## Differences from VS Code

- If a task is of type `"shell"`, and a custom shell is not defined, the parent
shell will be used.
- Only version 2.0.0 is supported.
- Does not support any extensions that add extra options/functionality
