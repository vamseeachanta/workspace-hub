"""
Coordination system for multi-agent task management

This package provides coordination capabilities for managing multiple agents
working on distributed tasks.
"""

__version__ = "0.1.0"

# Basic coordination classes that can be imported
class CoordinationError(Exception):
    """Base exception for coordination-related errors."""
    pass


class TaskManager:
    """Basic task manager for coordination testing."""

    def __init__(self):
        self.tasks = []
        self.agents = []

    def add_task(self, task):
        """Add a task to the manager."""
        self.tasks.append(task)
        return len(self.tasks) - 1

    def get_status(self):
        """Get the current status."""
        return {
            "active": True,
            "task_count": len(self.tasks),
            "agent_count": len(self.agents)
        }