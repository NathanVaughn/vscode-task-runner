"""Model classes for task runner dependency management."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, List, Optional, Union


@dataclass
class ShellQuotingOptionsEscape:
    # https://github.com/microsoft/vscode/blob/eef30e7165e19b33daa1e15e92fa34ff4a5df0d3/src/vs/workbench/contrib/tasks/common/tasks.ts#L70-L71
    escape_character: str
    characters_to_escape: List[str]


@dataclass
class ShellQuotingOptions:
    # https://github.com/microsoft/vscode/blob/eef30e7165e19b33daa1e15e92fa34ff4a5df0d3/src/vs/workbench/contrib/tasks/common/tasks.ts#L65-L83
    strong: Optional[str] = None
    escape: Optional[Union[ShellQuotingOptionsEscape, str]] = None
    weak: Optional[str] = None


class ShellQuoting(Enum):
    """
    Enum for shell quoting options
    """

    # https://github.com/microsoft/vscode/blob/eef30e7165e19b33daa1e15e92fa34ff4a5df0d3/src/vs/workbench/contrib/tasks/common/tasks.ts#L59-L60
    Strong = "strong"
    Weak = "weak"
    Escape = "escape"


class ShellType(Enum):
    SH = auto()
    PowerShell = auto()
    CMD = auto()
    WSL = auto()
    Unknown = auto()


@dataclass
class ShellConfiguration:
    executable: Optional[str] = None
    args: Optional[List[str]] = None
    quoting: Optional[ShellQuotingOptions] = None


@dataclass
class QuotedString:
    value: str
    quoting: ShellQuoting


CommandString = Union[str, QuotedString]
# https://github.com/microsoft/vscode/blob/eef30e7165e19b33daa1e15e92fa34ff4a5df0d3/src/vs/workbench/contrib/tasks/common/tasks.ts#L320


class ExecutionMode(Enum):
    """
    Defines how task dependencies should be executed.
    """

    SEQUENTIAL = "sequence"
    PARALLEL = "parallel"


@dataclass
class TaskNode:
    """
    Represents a node in the task dependency tree.

    This class is used to build a tree structure of tasks for more efficient
    execution management, particularly for complex task hierarchies with
    mixed sequential and parallel dependencies.
    """

    label: str
    task: Any  # Task object - avoid circular import
    execution_mode: ExecutionMode = ExecutionMode.SEQUENTIAL
    dependencies: List[TaskNode] = field(default_factory=list)
    visited: bool = False

    def add_dependency(self, dependency: TaskNode) -> None:
        """
        Add a dependency to this task node.

        Args:
            dependency: The task node to add as a dependency
        """
        self.dependencies.append(dependency)

    def mark_as_visited(self) -> None:
        """
        Mark this node as visited during tree traversal.
        """
        self.visited = True

    def is_visited(self) -> bool:
        """
        Check if this node has been visited during tree traversal.

        Returns:
            bool: True if the node has been visited, False otherwise
        """
        return self.visited

    def reset_visited(self) -> None:
        """
        Reset the visited flag for this node.
        """
        self.visited = False
