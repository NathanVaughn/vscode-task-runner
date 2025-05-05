"""Task executor module for managing task dependency trees and execution."""

import multiprocessing
from typing import Any, Dict, List, Optional, Set

import vscode_task_runner.printer
import vscode_task_runner.variables
from vscode_task_runner.models import ExecutionMode, TaskNode
from vscode_task_runner.task import Task


class TaskExecutor:
    """
    Class responsible for executing tasks with proper dependency management.

    This class builds a dependency tree from task definitions and executes
    the tasks according to their dependency order (sequential or parallel).
    """

    def __init__(self) -> None:
        """Initialize the TaskExecutor."""
        self.visited_tasks: Set[str] = set()

    def build_dependency_tree(self, task: Task) -> TaskNode:
        """
        Build a dependency tree starting from the given task.

        Args:
            task: The root task to build the tree from

        Returns:
            TaskNode: The root node of the dependency tree
        """
        # Create the root node
        execution_mode = ExecutionMode.SEQUENTIAL
        if task.depends_order == "parallel":
            execution_mode = ExecutionMode.PARALLEL

        root_node = TaskNode(label=task.label, task=task, execution_mode=execution_mode)

        # Process dependencies recursively
        for dependency in task.depends_on:
            dependency_node = self.build_dependency_tree(dependency)
            root_node.add_dependency(dependency_node)

        return root_node

    def execute_tree(
        self,
        root_node: TaskNode,
        inputs_data: Optional[List[Dict[str, Any]]] = None,
        extra_args: Optional[List[str]] = None,
    ) -> None:
        """
        Execute tasks according to the dependency tree structure.

        Args:
            root_node: The root node of the dependency tree
            inputs_data: Input variables data from tasks.json
            extra_args: Extra arguments to pass to the task
        """
        # Reset visited state for execution
        self._reset_visited_state(root_node)
        self.visited_tasks.clear()

        # Execute the tree starting from the root
        self._execute_node(root_node, inputs_data, extra_args, is_root=True)

    def _reset_visited_state(self, node: TaskNode) -> None:
        """
        Reset the visited flag for all nodes in the tree.

        Args:
            node: The current node to reset
        """
        node.reset_visited()
        for dependency in node.dependencies:
            self._reset_visited_state(dependency)

    def _execute_node(
        self,
        node: TaskNode,
        inputs_data: Optional[List[Dict[str, Any]]] = None,
        extra_args: Optional[List[str]] = None,
        task_color_index: int = 0,
        is_root: bool = False,
    ) -> None:
        """
        Execute a single node and its dependencies.

        Args:
            node: The node to execute
            inputs_data: Input variables data from tasks.json
            extra_args: Extra arguments to pass to the task
            task_color_index: Index used for color coding output
            is_root: Whether this is the root (top-level) task
        """
        # Skip if already visited (prevents circular dependencies)
        if node.is_visited() or node.label in self.visited_tasks:
            return

        # Mark as visited to avoid duplicate execution
        node.mark_as_visited()
        self.visited_tasks.add(node.label)

        # Handle different execution modes
        if node.execution_mode == ExecutionMode.PARALLEL and node.dependencies:
            self._execute_dependencies_in_parallel(node, inputs_data)
        else:
            # For sequential execution, pass increasing color indices
            color_idx = task_color_index
            for dependency in node.dependencies:
                # Don't pass extra_args to dependencies, only to the root task
                self._execute_node(dependency, inputs_data, None, color_idx)
                color_idx += 1

        # Execute the task itself if it's not a virtual task
        if not node.task.is_virtual:
            # Convert inputs_data to Dict[str, str] format for _execute_single_task
            input_vars_dict = None
            if inputs_data:
                # Process the inputs_data to get input variable values
                all_commands = [node.task.subprocess_command()]
                input_vars_dict = (
                    vscode_task_runner.variables.get_input_variables_values(
                        all_commands, inputs_data
                    )
                )

            # Only pass extra_args if this is the root task
            task_extra_args = extra_args if is_root else None

            self._execute_single_task(
                node.task,
                input_vars_dict,
                task_extra_args,
                color_index=task_color_index,
            )

    def _execute_dependencies_sequentially(
        self, node: TaskNode, inputs_data: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """
        Execute dependencies in sequential order.

        Args:
            node: The node whose dependencies to execute
            inputs_data: Input variables data from tasks.json
        """
        for dependency in node.dependencies:
            self._execute_node(dependency, inputs_data)

    def _execute_dependencies_in_parallel(
        self, node: TaskNode, inputs_data: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """
        Execute dependencies in parallel.

        Args:
            node: The node whose dependencies to execute
            inputs_data: Input variables data from tasks.json
        """
        # Get all dependency tasks
        dependency_tasks = [dep.task for dep in node.dependencies]

        # Get input variables and values
        all_commands = [
            t.subprocess_command() for t in dependency_tasks if not t.is_virtual
        ]
        input_vars_values = vscode_task_runner.variables.get_input_variables_values(
            all_commands, inputs_data
        )

        # Find default build task if any
        default_build_task = next(
            (t.label for t in dependency_tasks if t.is_default_build_task), None
        )

        # Log parallel execution
        vscode_task_runner.printer.info(
            f"Executing {len(dependency_tasks)} dependencies of task "
            f"{vscode_task_runner.printer.yellow(node.label)} in parallel"
        )

        # Execute tasks in parallel
        self._execute_tasks_parallel(
            dependency_tasks,
            input_vars_values=input_vars_values,
            default_build_task=default_build_task,
        )

        # Mark all dependencies as visited
        for dependency in node.dependencies:
            dependency.mark_as_visited()
            self.visited_tasks.add(dependency.label)

    def _execute_tasks_parallel(
        self,
        tasks: List[Task],
        input_vars_values: Optional[Dict[str, str]] = None,
        default_build_task: Optional[str] = None,
    ) -> None:
        """
        Execute multiple tasks in parallel.

        Args:
            tasks: List of tasks to execute in parallel
            input_vars_values: Input variables values
            default_build_task: Label of the default build task if any
        """
        # Use the existing parallel execution logic
        jobs = []
        for i, task in enumerate(tasks):
            if task.is_virtual:
                continue

            p = multiprocessing.Process(
                target=self._execute_single_task,
                args=(task, input_vars_values, None, default_build_task),
                kwargs={"color_index": i},  # Use task index as color index
            )
            jobs.append(p)
            p.start()

        # wait for all jobs to finish
        for job in jobs:
            job.join()

    def _execute_single_task(
        self,
        task: Task,
        input_vars_values: Optional[Dict[str, str]] = None,
        extra_args: Optional[List[str]] = None,
        default_build_task: Optional[str] = None,
        color_index: int = 0,
    ) -> None:
        """
        Execute a single task.

        Args:
            task: The task to execute
            input_vars_values: Input variables values
            extra_args: Extra arguments to pass to the task
            default_build_task: Label of the default build task if any
            color_index: Index used for color coding output
        """
        # Use the existing task execution logic but adapted for our needs
        from vscode_task_runner.executor import execute_task

        # Ensure input_vars_values is a dictionary
        if input_vars_values is not None and not isinstance(input_vars_values, dict):
            input_vars_values = {}

        execute_task(
            task,
            index=1,  # We don't track indices in this implementation
            total=1,  # We don't track total in this implementation
            input_vars_values=input_vars_values,
            default_build_task=default_build_task,
            extra_args=extra_args,
            color_index=color_index,  # Pass color index for consistent task coloring
        )
