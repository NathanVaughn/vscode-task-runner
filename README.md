# VSCode Task Runner

## Implemented Features

- [x] Predefined variables:
  - `${userHome}`
  - `${workspaceFolder}`
  - `${workspaceFolderBasename}`
  - `${pathSeparator}`
  - `${cwd}`
  - `${env:VARIABLE}`
- [x] Settings hierarchy:
  - Global level settings
  - Global level OS-specific settings
  - Task level settings
  - Task level OS-specific settings
- [x] Task configuration:
  - `cwd`
  - `env`
  - `type`
  - `command`
  - `args`
  - `shell`

## Unsupported Features

- Any predefined variable not listed above. The other variables tend to rely
  upon a file open VS Code, or VS Code itself.
- Problem matchers
- Background tasks
- UNC path conversion

## Differences from VS Code

- If a task is of type `"shell"`, and a custom shell is not defined, the parent
shell will be used.
- Only version 2.0.0 is currently supported.
