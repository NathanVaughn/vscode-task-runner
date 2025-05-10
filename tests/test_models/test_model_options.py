from vscode_task_runner.models.options import CommandOptions
from vscode_task_runner.models.shell import ShellConfiguration


def test_stringify_env() -> None:
    """
    Test the stringify_env function.
    """
    co = CommandOptions(
        env={
            "TEST1": "value1",
            "TEST2": "value2",
            "TEST3": 1234,
            "TEST5": True,
            "TEST6": False,  # type: ignore
        }
    )
    assert co.env == {
        "TEST1": "value1",
        "TEST2": "value2",
        "TEST3": "1234",
        "TEST5": "true",
        "TEST6": "false",
    }


def test_resolve_variables(default_build_task_mock: None) -> None:
    """
    Test resolving variables
    """

    co = CommandOptions(
        shell=ShellConfiguration(),
        cwd="${defaultBuildTask}",
        env={"TEST1": "${defaultBuildTask}"},
    )
    co.resolve_variables()
    assert co.cwd == "task1"
    assert co.env == {"TEST1": "task1"}
