from tests.conftest import load_task


def test_task_setting_os() -> None:
    task = load_task(__file__, "Test")
    assert task._get_task_setting("command") == "test2"
