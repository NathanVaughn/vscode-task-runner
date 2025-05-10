import pprint

from tests.conftest import task_obj
from vscode_task_runner import executor


def test_collect_levels() -> None:
    task_1_1 = task_obj(__file__, "Task_1_1")
    task_1_2 = task_obj(__file__, "Task_1_2")

    levels = executor.collect_levels([task_1_1, task_1_2])

    # Tree looks like
    # - Task_1_1
    # -- Task_2_1
    # --- Task_3_1
    # --- Task_3_2
    # -- Task_2_2
    # --- Task_3_3
    # - Task_1_2
    # -- Task_2_3

    pprint.pprint(levels)

    # first batch
    assert levels[0].tasks[0].label == "Task_3_1"
    assert levels[0].tasks[1].label == "Task_3_2"

    # second batch
    assert levels[1].tasks[0].label == "Task_3_3"

    # third batch
    assert levels[2].tasks[0].label == "Task_2_1"
    assert levels[2].tasks[1].label == "Task_2_2"

    # fourth batch
    assert levels[3].tasks[0].label == "Task_1_1"

    # fifth level
    assert levels[4].tasks[0].label == "Task_2_3"

    # last level
    assert levels[5].tasks[0].label == "Task_1_2"
