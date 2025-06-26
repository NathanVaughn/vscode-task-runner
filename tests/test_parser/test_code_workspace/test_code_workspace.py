from tests.conftest import tasks_obj


def test_code_workspace() -> None:
    tasks = tasks_obj(__file__)
    assert tasks.tasks[0].label == "test"
