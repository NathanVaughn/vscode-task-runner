import vscode_task_runner.executor
from tests.conftest import load_task


def test_depends_on() -> None:
    task = load_task(__file__, "Test1")
    all_tasks = vscode_task_runner.executor.collect_task(task)
    assert [d.label for d in all_tasks] == ["Test3", "Test5", "Test4", "Test2", "Test1"]
