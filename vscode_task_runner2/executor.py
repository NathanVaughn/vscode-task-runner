from vscode_task_runner2.models.execution_level import ExecutionLevel
from vscode_task_runner2.models.task import DependsOrderEnum, Task


def collect_levels(task: Task) -> list[ExecutionLevel]:
    """
    Given a task label, return the task and all child tasks, recursively.
    """
    execution_levels: list[ExecutionLevel] = []

    def _walk_tree(tree_task: Task) -> None:
        child_tasks = tree_task.depends_on

        # depth first search
        for child_task in child_tasks:
            _walk_tree(child_task)

        # add an execution level for the current task
        if child_tasks:
            execution_levels.append(
                ExecutionLevel(order=tree_task.depends_order, tasks=child_tasks)
            )

    # Add the current task to the execution levels
    execution_levels.append(
        ExecutionLevel(order=DependsOrderEnum.sequence, tasks=[task])
    )
    return execution_levels
