"""Initial PawPal+ class skeletons corresponding to diagrams/uml_draft.mmd.

Method bodies will be implemented in the next development stages.
"""

from dataclasses import dataclass, field
from datetime import date


@dataclass
class Task:
    """Represent one pet care activity and its scheduling information."""

    description: str
    time: str = "08:00"
    due_date: date = field(default_factory=date.today)
    duration_minutes: int = 20
    priority: str = "medium"
    frequency: str = "once"
    completed: bool = False

    def mark_complete(self):
        """Mark this occurrence complete and handle its recurrence."""
        raise NotImplementedError("Task behavior will be added in stage 2.")


@dataclass
class Pet:
    """Store a pet's identifying information and care tasks."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task):
        """Attach a care task to this pet."""
        raise NotImplementedError("Pet behavior will be added in stage 2.")

    def mark_task_complete(self, task_id: str):
        """Complete a task and retain any next occurrence."""
        raise NotImplementedError("Pet behavior will be added in stage 2.")


@dataclass
class Owner:
    """Group the pets cared for by one owner."""

    name: str
    preferred_species: str = ""
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet):
        """Register a pet with the owner."""
        raise NotImplementedError("Owner behavior will be added in stage 2.")

    def get_all_tasks(self) -> list:
        """Retrieve care tasks across the owner's pets."""
        raise NotImplementedError("Owner behavior will be added in stage 2.")


class Scheduler:
    """Organize and select care tasks across the household."""

    def __init__(self, owner: Owner):
        """Keep a reference to the household being scheduled."""
        self.owner = owner

    def sort_by_time(self) -> list:
        """Return tasks in chronological order."""
        raise NotImplementedError("Scheduling will be added in stage 3.")

    def filter_tasks(self) -> list:
        """Select tasks matching requested criteria."""
        raise NotImplementedError("Scheduling will be added in stage 3.")

    def detect_conflicts(self) -> list:
        """Identify overlapping care tasks."""
        raise NotImplementedError("Scheduling will be added in stage 3.")

    def build_plan(self) -> tuple:
        """Choose daily tasks within the owner's constraints."""
        raise NotImplementedError("Scheduling will be added in stage 3.")
