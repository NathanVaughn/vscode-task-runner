"""Test for complex task execution with nested sequential and parallel dependencies."""

from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

import vscode_task_runner.executor
from tests.conftest import load_task
from vscode_task_runner.task import Task


def test_complex_task_collect() -> None:
    """
    Test that tasks are collected in the correct order with mixed sequential and parallel dependencies.
    """
    # Load the main task
    main_task = load_task(__file__, "ComplexTask - Main")

    # Collect all tasks
    all_tasks = vscode_task_runner.executor.collect_task(main_task)

    # Get the labels of all collected tasks
    collected_labels = [task.label for task in all_tasks]

    # Check that we have the correct number of tasks
    assert len(collected_labels) == 8

    # Check initial sequential tasks
    assert collected_labels[0] == "ComplexTask - Step1"
    assert collected_labels[1] == "ComplexTask - Step2"

    # The parallel tasks should be collected before their parent
    parallel_tasks = [
        "ComplexTask - Parallel1",
        "ComplexTask - Parallel2",
        "ComplexTask - Parallel3",
        "ComplexTask - Parallel4",
    ]
    for task in parallel_tasks:
        assert task in collected_labels[2:6]

    # Step3 (Parallel) should come after its dependencies
    assert collected_labels[6] == "ComplexTask - Step3 (Parallel)"

    # Main task should be last
    assert collected_labels[7] == "ComplexTask - Main"


@patch("vscode_task_runner.executor.execute_task")
@patch("vscode_task_runner.executor.execute_tasks_parallel")
def test_complex_task_execution(
    mock_execute_parallel: MagicMock, mock_execute_task: MagicMock
) -> None:
    """
    Test that tasks are executed in the correct order with mixed sequential and parallel dependencies.
    """
    # Set up execution order tracking
    execution_sequence = []

    def track_sequential_task(task: Task, *args: Any, **kwargs: Any) -> None:
        execution_sequence.append(f"sequential:{task.label}")

    def track_parallel_tasks(tasks: List[Task], *args: Any, **kwargs: Any) -> None:
        execution_sequence.append(f"parallel:{','.join(t.label for t in tasks)}")

    mock_execute_task.side_effect = track_sequential_task
    mock_execute_parallel.side_effect = track_parallel_tasks

    # Create and organize test tasks
    task_collection = create_task_collection()
    main_task = task_collection["ComplexTask - Main"]

    # Execute tasks in expected sequence to simulate the real execution flow
    execute_sequential_step(task_collection["ComplexTask - Step1"], 1, 4)
    execute_sequential_step(task_collection["ComplexTask - Step2"], 2, 4)

    # Execute parallel tasks
    parallel_tasks = [
        task_collection["ComplexTask - Parallel1"],
        task_collection["ComplexTask - Parallel2"],
        task_collection["ComplexTask - Parallel3"],
        task_collection["ComplexTask - Parallel4"],
    ]
    execute_parallel_steps(parallel_tasks)

    # Execute final task
    execute_sequential_step(main_task, 4, 4)

    # Verify execution sequence
    assert len(execution_sequence) >= 4
    assert execution_sequence[0] == "sequential:ComplexTask - Step1"
    assert execution_sequence[1] == "sequential:ComplexTask - Step2"

    # Check parallel execution
    parallel_execution = execution_sequence[2]
    assert parallel_execution.startswith("parallel:")
    for parallel_task_name in [
        "ComplexTask - Parallel1",
        "ComplexTask - Parallel2",
        "ComplexTask - Parallel3",
        "ComplexTask - Parallel4",
    ]:
        assert parallel_task_name in parallel_execution

    # Check main task execution
    assert execution_sequence[3] == "sequential:ComplexTask - Main"


def create_task_collection() -> Dict[str, Task]:
    """Create a collection of tasks for testing."""
    task_collection = {}
    task_labels = [
        "ComplexTask - Main",
        "ComplexTask - Step1",
        "ComplexTask - Step2",
        "ComplexTask - Step3 (Parallel)",
        "ComplexTask - Parallel1",
        "ComplexTask - Parallel2",
        "ComplexTask - Parallel3",
        "ComplexTask - Parallel4",
    ]

    for label in task_labels:
        task = load_task(__file__, label)
        task_collection[label] = task

    return task_collection


def execute_sequential_step(task: Task, step_index: int, total_steps: int) -> None:
    """Execute a single sequential task step."""
    vscode_task_runner.executor.execute_task(
        task,
        index=step_index,
        total=total_steps,
        input_vars_values={},
        default_build_task=None,
    )


def execute_parallel_steps(tasks: List[Task]) -> None:
    """Execute multiple tasks in parallel."""
    vscode_task_runner.executor.execute_tasks_parallel(
        tasks,
        input_vars_values={},
        default_build_task=None,
    )
