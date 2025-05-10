from tests.conftest import task_obj


def test_non_unique() -> None:
    """
    Test duplicate labels in the tasks.json file
    """
    # also ensure no exception is raised if we don't touch the other task
    t = task_obj(__file__, "Task2")
    assert t.depends_on_labels == ["Task1"]
