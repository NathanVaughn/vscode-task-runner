import vtr.executor
from tests.conftest import load_task


def test_depends_on(
    linux: None,
) -> None:
    task = load_task(__file__, "Test1")
    all_tasks = vtr.executor.collect_task(task)
    assert [d.label for d in all_tasks] == ["Test3", "Test5", "Test4", "Test2", "Test1"]
