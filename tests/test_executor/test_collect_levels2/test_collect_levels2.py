import pprint

from tests.conftest import task_obj
from vscode_task_runner import executor


def test_collect_levels2() -> None:
    task_main = task_obj(__file__, "All")

    levels = executor.build_tasks_order([task_main])
    pp_levels = [[t.label for t in lev] for lev in levels]
    pprint.pprint(pp_levels)

    # https://github.com/NathanVaughn/vscode-task-runner/pull/108

    # first batch
    assert levels[0][0].label == "Sequence 1"
    assert levels[1][0].label == "Sequence 2"

    # second batch
    assert levels[2][0].label == "Parallel 1"
    assert levels[2][1].label == "Parallel 2"
    assert levels[2][2].label == "Parallel 3"

    # third batch
    assert levels[3][0].label == "Sequence 3"

    # fourth batch
    assert levels[4][0].label == "All"
