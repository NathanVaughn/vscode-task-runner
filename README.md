# VS Code Task Runner

[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![GitHub license](https://img.shields.io/github/license/NathanVaughn/vscode-task-runner)](https://github.com/NathanVaughn/vscode-task-runner/blob/main/LICENSE)
[![PyPi versions](https://img.shields.io/pypi/pyversions/vscode-task-runner)](https://pypi.org/project/vscode-task-runner)
[![PyPi downloads](https://img.shields.io/pypi/dm/vscode-task-runner)](https://pypi.org/project/vscode-task-runner)

---

This is a command-line tool to execute VS Code
[tasks](https://code.visualstudio.com/docs/editor/tasks)
defined in the `.vscode/tasks.json` file.
This allows you to write tasks once, and be able to run them in your editor,
and in CI/CD. Basically, use `.vscode/tasks.json` as a Makefile.

This tool aims to be as feature-complete as possible with what VS Code supports for
Windows, MacOSX and Linux. Much of the logic is taken directly from the VS Code
source code and reimplemented in Python.

This pairs well with VS Code extensions that add buttons to run tasks such as
[actboy168.tasks](https://marketplace.visualstudio.com/items?itemName=actboy168.tasks).

## Usage

Python 3.8+ is required.

Install with pip/pipx:

```bash
pip install vscode-task-runner
```

Use the command `vtr` on the command line and provide the label of the task(s).
There must be a `.vscode/tasks.json` file in the working directory you run the
command in. (You can also use the `vscode-task-runner` command instead
if it makes you feel better).

## Examples

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "pre-commit",
      "type": "shell",
      "command": "poetry run pre-commit run --all-files"
    }
  ]
}
```

```shell
$ vtr pre-commit
[1/1] Executing task "pre-commit": C:\Program Files\WindowsApps\Microsoft.PowerShell_7.3.4.0_x64__8wekyb3d8bbwe\pwsh.exe -Command poetry run pre-commit run --all-files
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

Additionally, for convenience, extra arguments can be tacked on to a task.
For example, you can add extra settings or overrides when running in CI/CD.
Continuing the example above:

```bash
$ vtr pre-commit --extra-args="--color=always" --extra-args="--show-diff-on-failure"
[1/1] Executing task "pre-commit": C:\Program Files\WindowsApps\Microsoft.PowerShell_7.3.4.0_x64__8wekyb3d8bbwe\pwsh.exe -Command poetry run pre-commit run --all-files --color=always --show-diff-on-failure
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

This can only be used when running a single task.

The `dependsOn` key is also supported:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "install",
      "type": "shell",
      "command": "poetry install --sync"
    },
    {
      "label": "build",
      "type": "shell",
      "command": "poetry build",
      "dependsOn": ["install"]
    }
  ]
}
```

```bash
$ vtr build
[1/2] Executing task "install": C:\Program Files\WindowsApps\Microsoft.PowerShell_7.3.4.0_x64__8wekyb3d8bbwe\pwsh.exe -Command poetry install --sync
Installing dependencies from lock file

No dependencies to install or update

Installing the current project: vscode-task-runner (0.1.1)
[2/2] Executing task "build": C:\Program Files\WindowsApps\Microsoft.PowerShell_7.3.4.0_x64__8wekyb3d8bbwe\pwsh.exe -Command poetry build
Building vscode-task-runner (0.1.1)
  - Building sdist
  - Built vscode_task_runner-0.1.1.tar.gz
  - Building wheel
  - Built vscode_task_runner-0.1.1-py3-none-any.whl
```

You can also use it as a [pre-commit](https://pre-commit.com) hook if desired:

```yaml
repos:
  - repo: https://github.com/NathanVaughn/vscode-task-runner
    rev: v0.1.3
    hooks:
      - id: vtr
        # Optionally override the hook name here
        # name: Build & Test
        args:
          - build # put the tasks you want to run here
          - test
```

The pre-commit hook does not match on any file types, and and will always execute.

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
    - `executable`
    - `args`
  - `dependsOn`
- Quoting support:
  - `"escape"`
  - `"strong"`
  - `"weak"`

## Unsupported Features

- Any predefined variable not listed above. The other variables tend to rely
  upon the specific file opened in VS Code, or VS Code itself.
- Problem matchers
- Background tasks
- UNC path conversion
- Parallel `dependsOn` task execution
- Task types other than `"process"` or `"shell"`

## Differences from VS Code

- If a task is of type `"shell"`, and a specific shell is not defined, the parent
  shell will be used
- Only schema version 2.0.0 is supported
- If no `cwd` is specified, the current working directory is used for the task instead
- Does not support any extensions that add extra options/functionality
- Does not load any VS Code settings
- `--extra-args` option
