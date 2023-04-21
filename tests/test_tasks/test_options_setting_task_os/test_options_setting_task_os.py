from tests.conftest import load_task


def test_options_setting_task_os(windows: None) -> None:
    task = load_task(__file__, "Test")
    assert task._get_options_setting("cwd") == "/test4/"
