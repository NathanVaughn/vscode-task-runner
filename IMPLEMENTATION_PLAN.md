# Implementation Plan: CLI Options for Input Fields

**Issue:** #124
**Goal:** Add CLI flag syntax like `vtr task_name --input-x=y` to provide input values without interactive prompts or environment variables.

## Current State Analysis

### How Inputs Currently Work

1. **Input Definition** (`models/input.py`):
   - Inputs are defined in `tasks.json` with type, id, description, options, etc.
   - Two supported types: `promptString` and `pickString`

2. **Input Resolution** (`variables/resolve.py`):
   - When `${input:id}` is encountered during variable resolution:
     1. First checks for `VTR_INPUT_{id}` environment variable
     2. If found, validates it against input constraints
     3. If not found, prompts user interactively using `questionary`
   - Results are cached via `@cache` decorator

3. **Environment Variable Approach**:
   - Currently supported: `VTR_INPUT_{id}=value vtr task_name`
   - **Problem:** Doesn't work reliably in Windows Command Prompt
   - Validation happens in `get_input_value()` function

### Current CLI Architecture

**Entry Point:** `console.py:run()`

**Argument Parsing:** `console.py:parse_args()`
- Uses `argparse.ArgumentParser`
- Currently supports:
  - `--skip-summary`: Sets `VTR_SKIP_SUMMARY=1`
  - `--continue-on-error`: Sets `VTR_CONTINUE_ON_ERROR=1`
  - `--complete`: Bash completion support
  - `--`: Separator for extra args to tasks

**Pattern:** CLI flags → Environment variables → Consumed by execution logic

## Requirements

From issue #124:

1. ✅ Add CLI flag syntax: `vtr task_name --input-x=y`
2. ✅ Values must match options defined in tasks.json (validation)
3. ✅ Support multiple input flags
4. ✅ CLI arguments take precedence over environment variables
5. ✅ Cross-platform compatibility (especially Windows Command Prompt)

## Implementation Strategy

### Approach: Custom Argument Parsing with Prefix Detection

Since input IDs are dynamic (defined in tasks.json), we need a flexible approach:

1. **Parse known arguments first** (task names, `--skip-summary`, etc.)
2. **Identify `--input-*` arguments** from remaining unknown args
3. **Set environment variables** before task execution
4. **Leverage existing validation** in `variables/resolve.py`

This minimizes changes and reuses the robust input validation logic already in place.

### Why Not Use argparse's add_argument?

- Input IDs are defined in tasks.json, not known at CLI parsing time
- Would require loading tasks.json before parsing CLI args (circular dependency)
- Custom parsing for `--input-*` prefix is simpler and more flexible

## Detailed Implementation Plan

### Phase 1: Argument Parsing Enhancement

**File:** `vscode_task_runner/console.py`

#### Step 1.1: Update `parse_args()` Function

**Current signature:**
```python
def parse_args(sys_argv: List[str], task_choices: List[str]) -> ArgParseResult
```

**Changes:**
1. Add `parse_known_args()` to capture unknown arguments
2. Parse `--input-<id>=<value>` from unknown args
3. Return input dict in `ArgParseResult`

**Implementation:**
```python
def parse_args(sys_argv: List[str], task_choices: List[str]) -> ArgParseResult:
    # ... existing ArgumentParser setup ...

    # Parse known args, capture unknown
    args, unknown = parser.parse_known_args(sys_argv)

    # Parse --input-* flags from unknown args
    input_values = {}
    remaining_unknown = []

    for arg in unknown:
        if arg.startswith("--input-"):
            # Handle --input-id=value
            if "=" in arg:
                key_part = arg[8:]  # Remove "--input-" prefix
                input_id, value = key_part.split("=", 1)
                input_values[input_id] = value
            else:
                raise ValueError(f"Invalid input flag format: {arg}. Expected: --input-<id>=<value>")
        else:
            remaining_unknown.append(arg)

    # Use remaining_unknown for extra_args processing (existing logic)
    # ... rest of function ...

    return ArgParseResult(
        task_labels=args.task_labels,
        extra_args=extra_args,
        input_values=input_values  # NEW
    )
```

**Edge Cases to Handle:**
- Input ID contains special characters (hyphens, underscores)
- Value contains `=` character (use `split("=", 1)`)
- Missing value (`--input-id` without `=value`)
- Duplicate input flags (last one wins? or error?)

#### Step 1.2: Update `ArgParseResult` Model

**File:** `vscode_task_runner/models/arg_parser.py`

**Changes:**
```python
class ArgParseResult(BaseModel):
    task_labels: list[str]
    extra_args: list[str]
    input_values: dict[str, str] = {}  # NEW: {input_id: value}
```

### Phase 2: Environment Variable Setting

**File:** `vscode_task_runner/console.py`

#### Step 2.1: Add `set_input_environment_variables()` Function

**Purpose:** Convert CLI input args to environment variables

**Implementation:**
```python
def set_input_environment_variables(input_values: dict[str, str]) -> None:
    """
    Set VTR_INPUT_* environment variables from CLI arguments.

    CLI arguments take precedence over existing environment variables.

    Args:
        input_values: Dictionary mapping input IDs to values
    """
    for input_id, value in input_values.items():
        env_var_name = f"VTR_INPUT_{input_id}"
        os.environ[env_var_name] = value
```

**Precedence Behavior:**
- CLI args override existing `VTR_INPUT_*` env vars (by setting os.environ)
- This matches requirement #4: "CLI arguments should take precedence"

#### Step 2.2: Call in `run()` Function

**Location:** `console.py:run()`

**Changes:**
```python
def run() -> int:
    # ... existing code to load tasks ...

    # Parse CLI arguments
    arg_parse_result = parse_args(sys.argv[1:], all_task_choices)

    # Set input environment variables from CLI args (NEW)
    set_input_environment_variables(arg_parse_result.input_values)

    # ... rest of execution ...
```

**Placement:** After parsing, before task execution (so inputs are resolved correctly)

### Phase 3: Input Validation Integration

**File:** `vscode_task_runner/variables/resolve.py`

#### Analysis: No Changes Needed!

The existing `get_input_value()` function already:
1. Checks `VTR_INPUT_{input_id}` environment variable first
2. Validates against input type constraints (pickString options, etc.)
3. Raises `BadInputEnvironmentVariable` if validation fails

**Validation Logic:**
```python
# Line 64-73 in resolve.py
env_var_name = f"VTR_INPUT_{input_id}"
env_value = os.getenv(env_var_name)

if env_value is not None:
    if input_obj.type_ == InputTypeEnum.PICK_STRING:
        options = [get_choice_value(opt) for opt in input_obj.options]
        check_item_with_options(env_value, options)
    return env_value
```

This will automatically validate CLI-provided inputs!

**Exception Handling:**
- `BadInputEnvironmentVariable`: Invalid value for pickString
- `UnsupportedInput`: Unsupported input type (command)

These exceptions are already caught and displayed in `console.py:run()` (line 104-109)

### Phase 4: Error Messages and User Experience

**File:** `vscode_task_runner/console.py`

#### Step 4.1: Improve Error Messages for CLI Inputs

**Current:**
```python
except exceptions.BadInputEnvironmentVariable as exc:
    stderr.print(str(exc), style=style.ERROR)
    return 1
```

**Enhancement:** Differentiate between env var and CLI arg errors

```python
except exceptions.BadInputEnvironmentVariable as exc:
    error_msg = str(exc)
    # Check if error is from CLI arg (input_id in arg_parse_result.input_values)
    if input_id_from_error in arg_parse_result.input_values:
        stderr.print(
            f"Invalid CLI input: {error_msg}\n"
            f"Hint: Use --input-{input_id}=<value> where value is one of the valid options.",
            style=style.ERROR
        )
    else:
        stderr.print(error_msg, style=style.ERROR)
    return 1
```

**Note:** May need to enhance `BadInputEnvironmentVariable` exception to include `input_id`

#### Step 4.2: Help Text Update

**File:** `vscode_task_runner/console.py`

**Update argument parser help:**
```python
parser = argparse.ArgumentParser(
    prog="vtr",
    description="...",
    epilog="""
Additional options:
  --input-<id>=<value>     Provide input value for input with ID <id>
                           (can be specified multiple times)
  --                       All arguments after this are passed to the task
"""
)
```

### Phase 5: Documentation

**Files to Update:**

1. **README.md:**
   - Add section on "Providing Input Values via CLI"
   - Show examples: `vtr build --input-environment=production`
   - Explain precedence: CLI args > env vars > interactive prompt

2. **CLI Help Text:**
   - Already covered in Phase 4.2

**Example Documentation:**

```markdown
### Providing Input Values

Inputs can be provided in three ways (in order of precedence):

1. **CLI Arguments** (cross-platform, recommended):
   ```bash
   vtr build --input-environment=production --input-region=us-west
   ```

2. **Environment Variables** (Linux/macOS):
   ```bash
   VTR_INPUT_environment=production vtr build
   ```

3. **Interactive Prompts** (default):
   The CLI will prompt you for any missing inputs.

#### CLI Argument Syntax

- Format: `--input-<id>=<value>`
- Multiple inputs: Repeat the flag
- Input IDs: Defined in your `.vscode/tasks.json` file
- Validation: Values must match options for `pickString` type inputs

#### Examples

```bash
# Single input
vtr deploy --input-target=staging

# Multiple inputs
vtr build --input-env=prod --input-platform=linux --input-arch=amd64

# Combined with task dependencies
vtr test:all --input-browser=chrome --continue-on-error
```
```

### Phase 6: Testing

#### Test Files to Create/Update

**6.1: Unit Tests for Argument Parsing**

**File:** `tests/test_console/test_parse_args.py`

**New Test Cases:**
```python
def test_parse_args_with_single_input():
    """Test parsing single --input-id=value flag"""
    result = parse_args(["task1", "--input-foo=bar"], ["task1"])
    assert result.input_values == {"foo": "bar"}

def test_parse_args_with_multiple_inputs():
    """Test parsing multiple --input-* flags"""
    result = parse_args(
        ["task1", "--input-env=prod", "--input-region=us-west"],
        ["task1"]
    )
    assert result.input_values == {"env": "prod", "region": "us-west"}

def test_parse_args_input_with_equals_in_value():
    """Test value containing = character"""
    result = parse_args(["task1", "--input-key=value=with=equals"], ["task1"])
    assert result.input_values == {"key": "value=with=equals"}

def test_parse_args_input_with_special_chars():
    """Test input ID with hyphens and underscores"""
    result = parse_args(
        ["task1", "--input-my-input_v2=value"],
        ["task1"]
    )
    assert result.input_values == {"my-input_v2": "value"}

def test_parse_args_input_without_value():
    """Test error when --input-id is missing =value"""
    with pytest.raises(ValueError, match="Invalid input flag format"):
        parse_args(["task1", "--input-foo"], ["task1"])

def test_parse_args_input_with_empty_value():
    """Test --input-id= with empty value"""
    result = parse_args(["task1", "--input-foo="], ["task1"])
    assert result.input_values == {"foo": ""}

def test_parse_args_input_duplicate_flags():
    """Test behavior with duplicate input flags (last wins)"""
    result = parse_args(
        ["task1", "--input-env=dev", "--input-env=prod"],
        ["task1"]
    )
    assert result.input_values == {"env": "prod"}

def test_parse_args_input_combined_with_other_flags():
    """Test --input-* combined with --skip-summary, etc."""
    result = parse_args(
        ["task1", "--skip-summary", "--input-env=prod", "--continue-on-error"],
        ["task1"]
    )
    assert result.task_labels == ["task1"]
    assert result.input_values == {"env": "prod"}
    assert os.environ.get("VTR_SKIP_SUMMARY") == "1"
    assert os.environ.get("VTR_CONTINUE_ON_ERROR") == "1"

def test_parse_args_input_with_extra_args():
    """Test --input-* combined with -- extra args"""
    result = parse_args(
        ["task1", "--input-env=prod", "--", "-v", "--output=file.txt"],
        ["task1"]
    )
    assert result.input_values == {"env": "prod"}
    assert result.extra_args == ["-v", "--output=file.txt"]
```

**6.2: Integration Tests for Input Resolution**

**File:** `tests/test_variables/test_resolve.py` (or new file `test_cli_inputs.py`)

**New Test Cases:**
```python
def test_cli_input_precedence_over_env_var():
    """Test CLI input overrides environment variable"""
    # Set env var
    os.environ["VTR_INPUT_foo"] = "env_value"

    # Simulate CLI input setting
    set_input_environment_variables({"foo": "cli_value"})

    # Check that CLI value is used
    assert os.environ["VTR_INPUT_foo"] == "cli_value"

def test_cli_input_pickstring_validation():
    """Test CLI input validated against pickString options"""
    # Setup input in INPUTS registry
    INPUTS["test_input"] = Input(
        type="pickString",
        id="test_input",
        options=["option1", "option2"]
    )

    # Set CLI input with valid value
    os.environ["VTR_INPUT_test_input"] = "option1"
    result = get_input_value("test_input")
    assert result == "option1"

    # Set CLI input with invalid value
    os.environ["VTR_INPUT_test_input"] = "invalid"
    with pytest.raises(BadInputEnvironmentVariable):
        get_input_value("test_input")

def test_cli_input_promptstring_accepts_any():
    """Test CLI input for promptString accepts any value"""
    INPUTS["test_input"] = Input(
        type="promptString",
        id="test_input"
    )

    os.environ["VTR_INPUT_test_input"] = "any value here!"
    result = get_input_value("test_input")
    assert result == "any value here!"
```

**6.3: End-to-End Tests**

**File:** `tests/test_console/test_e2e_cli_inputs.py` (new file)

**Test Cases:**
```python
def test_e2e_task_with_cli_input(tmp_path, monkeypatch):
    """Test full task execution with CLI input"""
    # Create tasks.json with input
    tasks_json = {
        "version": "2.0.0",
        "tasks": [
            {
                "label": "echo-input",
                "type": "shell",
                "command": "echo ${input:myinput}"
            }
        ],
        "inputs": [
            {
                "id": "myinput",
                "type": "promptString",
                "description": "My Input"
            }
        ]
    }

    # Write tasks.json
    tasks_file = tmp_path / ".vscode" / "tasks.json"
    tasks_file.parent.mkdir(parents=True)
    tasks_file.write_text(json.dumps(tasks_json))

    # Change to temp directory
    monkeypatch.chdir(tmp_path)

    # Run with CLI input
    sys.argv = ["vtr", "echo-input", "--input-myinput=test_value"]
    exit_code = run()

    assert exit_code == 0
    # Verify input was used (check stdout or task execution result)

def test_e2e_invalid_pickstring_cli_input(tmp_path, monkeypatch):
    """Test error handling for invalid pickString CLI input"""
    tasks_json = {
        "version": "2.0.0",
        "tasks": [
            {
                "label": "task1",
                "type": "shell",
                "command": "echo ${input:env}"
            }
        ],
        "inputs": [
            {
                "id": "env",
                "type": "pickString",
                "description": "Environment",
                "options": ["dev", "staging", "prod"]
            }
        ]
    }

    tasks_file = tmp_path / ".vscode" / "tasks.json"
    tasks_file.parent.mkdir(parents=True)
    tasks_file.write_text(json.dumps(tasks_json))

    monkeypatch.chdir(tmp_path)

    # Run with invalid CLI input
    sys.argv = ["vtr", "task1", "--input-env=production"]
    exit_code = run()

    assert exit_code == 1
    # Verify error message was shown
```

**6.4: Test Coverage Goals**

- Argument parsing: 100% coverage for new code paths
- Error handling: All exception cases tested
- Edge cases: Special characters, empty values, duplicates
- Integration: Full workflow from CLI → env vars → validation → execution

## Implementation Checklist

### Code Changes

- [ ] **Phase 1.1:** Update `parse_args()` to parse `--input-*` flags
- [ ] **Phase 1.2:** Add `input_values` field to `ArgParseResult` model
- [ ] **Phase 2.1:** Create `set_input_environment_variables()` function
- [ ] **Phase 2.2:** Call env setter in `run()` function
- [ ] **Phase 4.1:** Improve error messages for CLI input validation failures
- [ ] **Phase 4.2:** Update help text and epilog in argument parser

### Testing

- [ ] **Phase 6.1:** Add unit tests for argument parsing (8 test cases)
- [ ] **Phase 6.2:** Add integration tests for input resolution (3 test cases)
- [ ] **Phase 6.3:** Add end-to-end tests (2 test cases)
- [ ] Verify all existing tests still pass
- [ ] Check test coverage meets project standards

### Documentation

- [ ] **Phase 5:** Update README.md with CLI input examples
- [ ] Update CHANGELOG.md (if exists)
- [ ] Add docstrings to new functions

### Quality Assurance

- [ ] Test on Linux
- [ ] Test on Windows (Command Prompt and PowerShell)
- [ ] Test on macOS
- [ ] Verify precedence: CLI args > env vars > interactive prompt
- [ ] Test with special characters in input IDs and values
- [ ] Test error messages are helpful and clear

## Risk Analysis

### Low Risk

- **Leverage existing validation:** No changes to `variables/resolve.py` needed
- **Consistent pattern:** Follows same approach as `--skip-summary` flag
- **Minimal changes:** Only touches argument parsing and env var setting

### Potential Issues

1. **Input ID naming conflicts:**
   - User might have input IDs with spaces or special chars
   - Mitigation: Document supported characters, validate in parser

2. **Argument parsing ambiguity:**
   - `--input-*` might conflict with future flags
   - Mitigation: Reserve `--input-` prefix, document clearly

3. **Windows compatibility:**
   - Need to verify env var setting works on Windows
   - Mitigation: Test on Windows platform (primary goal of feature)

4. **Backwards compatibility:**
   - Ensure existing `VTR_INPUT_*` env vars still work
   - Mitigation: CLI args override but don't break env var usage

## Success Criteria

✅ **Feature Complete:**
- Users can provide inputs via `--input-<id>=<value>` syntax
- Multiple inputs supported
- CLI args take precedence over env vars
- Works on Windows Command Prompt

✅ **Quality:**
- All tests pass (new and existing)
- Test coverage ≥ 90% for new code
- Error messages are clear and helpful

✅ **Documentation:**
- README.md updated with examples
- Help text shows new option
- Docstrings added to new functions

✅ **Platform Compatibility:**
- Tested on Linux, Windows, macOS
- Works in Command Prompt, PowerShell, Bash, Zsh

## Timeline Estimate

- **Phase 1-2 (Core Implementation):** 2-3 hours
- **Phase 3-4 (Validation & UX):** 1-2 hours
- **Phase 5 (Documentation):** 1 hour
- **Phase 6 (Testing):** 3-4 hours
- **Total:** 7-10 hours (1-2 days)

## Future Enhancements (Out of Scope)

- Short form flags: `-i key=value` (alias for `--input-key=value`)
- JSON input file: `--input-file=inputs.json`
- Environment-specific input files: `.vtr.inputs.dev.json`
- Tab completion for input IDs
- Validation of input IDs against tasks.json before execution

---

**End of Implementation Plan**
