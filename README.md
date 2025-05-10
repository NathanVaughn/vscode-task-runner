# VS Code Task Runner

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
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

Python 3.9+ is required.

Install with [pipx](https://pipx.pypa.io/stable/) or [uv](https://docs.astral.sh/uv/):

```bash
pipx install vscode-task-runner
# or
uv tool install vscode-task-runner
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
[1/1] Executing task pre-commit: /bin/bash -c uv run pre-commit run --all-files
check json5..............................................................Passed
check toml...............................................................Passed
check yaml...............................................................Passed
check for case conflicts.................................................Passed
trim trailing whitespace.................................................Passed
check for merge conflicts................................................Passed
mixed line ending........................................................Passed
uv-lock..................................................................Passed
ruff.....................................................................Passed
ruff-format..............................................................Passed
pyright..................................................................Passed
markdownlint.............................................................Passed
```

Additionally, for convenience, extra arguments can be tacked on to a task.
For example, you can add extra settings or overrides when running in CI/CD.
Continuing the example above:

```bash
$ vtr pre-commit --color=always --show-diff-on-failure
[1/1] Executing task pre-commit: /bin/bash -c uv run pre-commit run --all-files --color=always --show-diff-on-failure
check json5..............................................................Passed
check toml...............................................................Passed
check yaml...............................................................Passed
check for case conflicts.................................................Passed
trim trailing whitespace.................................................Passed
check for merge conflicts................................................Passed
mixed line ending........................................................Passed
uv-lock..................................................................Passed
ruff.....................................................................Passed
ruff-format..............................................................Passed
pyright..................................................................Passed
markdownlint.............................................................Passed
```

This can only be used when running a single task. You can also use `--` as a separator
to add additional arguments that do not start with a `--`. Example:

```bash
$ vtr test -- option1 option2
# This will run the task "test" with the arguments "option1" and "option2"
```

If your task uses an `${input:id}` variable, you can provide the value for
this variable as an environment variable named `VTR_INPUT_{id}`. Example:

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "tests",
            "command": "pytest --cov=vtr/ --cov-report ${input:report_format}",
            "type": "shell"
        }
    ],
    "inputs": [
        {
            "id": "report_format",
            "description": "Coverage report format",
            "type": "pickString",
            "options": [
                "html",
                "xml",
                "annotate",
                "json",
                "lcov"
            ]
        }
    ]
}
```

Then in GitHub Actions:

```yaml
  - name: Run tests
    run: vtr tests
    env:
      VTR_INPUT_report_format: html
```

Similarly, if more than one default build task is defined, the
`VTR_DEFAULT_BUILD_TASK` environment variable can be used to specify which one
to use. Otherwise, you will be interactively prompted to select one.

The `dependsOn` key is also supported:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "install",
      "type": "shell",
      "command": "uv sync"
    },
    {
      "label": "build",
      "type": "shell",
      "command": "uv build",
      "dependsOn": ["install"]
    }
  ]
}
```

```bash
$ vtr build
[1/2] Executing task install: /bin/bash -c uv sync
Resolved 30 packages in 0.52ms
Audited 28 packages in 0.05ms
[2/2] Executing task build: /bin/bash -c uv build
Building source distribution...
Building wheel from source distribution...
Successfully built dist/vscode_task_runner-2.0.0.tar.gz
Successfully built dist/vscode_task_runner-2.0.0-py3-none-any.whl
```

You can also use it as a [pre-commit](https://pre-commit.com) hook if desired:

```yaml
repos:
  - repo: https://github.com/NathanVaughn/vscode-task-runner
    rev: v2.0.0
    hooks:
      - id: vtr
        # Optionally override the hook name here
        # name: Build & Test
        args:
          - build # put the tasks you want to run here
          - test
```

The pre-commit hook does not match on any file types, and and will always execute.

If using `pre-commit` and `poetry` is part of your task, you may need to add the
following

```json
"options": {
    "env": {
        "VIRTUAL_ENV": "${workspaceFolder}${pathSeparator}.venv"
    }
}
```

and set [`virtualenvs.in-project`](https://python-poetry.org/docs/configuration/#virtualenvsin-project)
to `true`.

Otherwise, `poetry` may think the `pre-commit` virtual environment is your
project's virtual environment.

## Implemented Features

- [Predefined variables](https://code.visualstudio.com/docs/reference/variables-reference#_predefined-variables):
  - `${userHome}`
  - `${workspaceRoot}`
  - `${workspaceFolder}`
  - `${workspaceFolderBasename}`
  - `${pathSeparator}`
  - `${/}`
  - `${defaultBuildTask}`
  - `${cwd}`
  - `${env:VARIABLE}`
  - `${input:VARIABLE}`
- Settings hierarchy:
  - Global level settings
  - Global level OS-specific settings
  - Task level settings
  - Task level OS-specific settings
- Task configuration:
  - `type`
    - `"process"`
    - `"shell"`
  - `command`
  - `options`
    - `shell`
      - `executable`
      - `args`
    - `cwd`
    - `env`
  - `args`
  - `dependsOn`
- Quoting support:
  - `"escape"`
  - `"strong"`
  - `"weak"`

## Unsupported Features

- Any predefined variable not listed above. The other variables tend to rely
  upon the specific file opened in VS Code, or VS Code itself.
- Variables scoped to workspace folders
- Command variables
- Input command variables
- Problem matchers
- Background tasks
- UNC path conversion
- Parallel `dependsOn` task execution (Coming soon!)
- Task types other than `"process"` or `"shell"` (such as `"npm"`, `"docker"`, etc.)

## Differences from VS Code

- If a task is of type `"shell"`, and a specific shell is not defined, the parent
  shell will be used
- Only schema version 2.0.0 is supported
- If no `cwd` is specified, the current working directory is used for the task instead
- Does not support deprecated options (`isShellCommand`, `isBuildCommand`)
- Does not support any extensions that add extra options/functionality
- Does not load any VS Code settings
- Extra arguments option
- `VTR_INPUT_${id}` environment variables
- `VTR_DEFAULT_BUILD_TASK` environment variable

## Similar Projects

- [vstask](https://github.com/cmccandless/vstask)
- [overseer.nvim](https://github.com/stevearc/overseer.nvim/blob/master/doc/guides.md#vs-code-tasks)
