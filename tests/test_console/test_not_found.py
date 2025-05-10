import os

from pytest import CaptureFixture

from vscode_task_runner.console import run


def test_not_found(capsys: CaptureFixture) -> None:
    """
    Test the not found error
    """
    # change to some directory that exists but wihtout tasks.json
    current_cwd = os.getcwd()
    os.chdir(os.path.expanduser("~"))

    # run the console
    assert run() == 1

    # change back to original directory to not break other tests
    os.chdir(current_cwd)

    # doesn't raise an excpetion, but prints error and exits
    captured = capsys.readouterr()
    assert "tasks.json" in captured.out
