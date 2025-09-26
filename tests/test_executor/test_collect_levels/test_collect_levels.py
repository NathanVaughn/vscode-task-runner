import pprint

from tests.conftest import task_obj
from vscode_task_runner import executor


def test_collect_levels() -> None:
    task_1_1 = task_obj(__file__, "Task_1_1")
    task_1_2 = task_obj(__file__, "Task_1_2")

    levels = executor.build_tasks_order([task_1_1, task_1_2])
    pp_levels = [[t.label for t in lev] for lev in levels]
    pprint.pprint(pp_levels)

    # Tree looks like
    # - Task_1_1
    # -- Task_2_1
    # --- Task_3_1
    # --- Task_3_2
    # -- Task_2_2
    # --- Task_3_3
    # - Task_1_2
    # -- Task_2_3

    # first batch
    assert levels[0][0].label == "Task_3_1"
    assert levels[0][1].label == "Task_3_2"

    # second batch
    assert levels[1][0].label == "Task_2_1"

    # third batch
    assert levels[2][0].label == "Task_3_3"

    # fourth batch
    assert levels[3][0].label == "Task_2_2"

    # fifth batch
    assert levels[4][0].label == "Task_1_1"

    # sixth batch
    assert levels[5][0].label == "Task_2_3"

    # last level
    assert levels[6][0].label == "Task_1_2"
