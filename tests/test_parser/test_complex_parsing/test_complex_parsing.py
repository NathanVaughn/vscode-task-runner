from tests.conftest import tasks_obj
from vscode_task_runner.variables.runtime import RUNTIME_VARIABLES


def test_parsing() -> None:
    # make sure it parses with no errors
    tasks_obj(__file__)
    assert RUNTIME_VARIABLES["${defaultBuildTask}"] == "Task 1"
