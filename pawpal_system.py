"""Pet care models and scheduling rules, independent of Streamlit."""

from dataclasses import dataclass, field, replace
from datetime import date, datetime, timedelta
import re
from uuid import uuid4

PRIORITIES = {"high": 0, "medium": 1, "low": 2}
FREQUENCIES = {"once": 0, "daily": 1, "weekly": 7}


def require_text(value: str, label: str) -> str:
    """Validate and trim required text."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} is required.")
    return value.strip()


@dataclass
class Task:
    """One dated occurrence of a pet care activity."""

    description: str
    time: str = "08:00"
    due_date: date = field(default_factory=date.today)
    duration_minutes: int = 20
    priority: str = "medium"
    frequency: str = "once"
    completed: bool = False
    id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self):
        """Reject invalid task data at the model boundary."""
        self.description = require_text(self.description, "Task description")
        if not isinstance(self.time, str) or not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", self.time):
            raise ValueError("Time must use 24-hour HH:MM format.")
        if type(self.due_date) is not date:
            raise ValueError("Due date must be a date.")
        if type(self.duration_minutes) is not int or not 1 <= self.duration_minutes <= 1440:
            raise ValueError("Duration must be between 1 and 1440 whole minutes.")
        if self.priority not in PRIORITIES:
            raise ValueError("Priority must be high, medium, or low.")
        if self.frequency not in FREQUENCIES:
            raise ValueError("Frequency must be once, daily, or weekly.")

    @property
    def start(self) -> datetime:
        """Return the dated start time for comparison."""
        return datetime.combine(self.due_date, datetime.strptime(self.time, "%H:%M").time())

    @property
    def end(self) -> datetime:
        """Return the exclusive end time, including overnight durations."""
        return self.start + timedelta(minutes=self.duration_minutes)

    def mark_complete(self, today: date | None = None) -> "Task | None":
        """Complete once and return the next occurrence of a recurring task."""
        if self.completed:
            return None
        self.completed = True
        interval = FREQUENCIES[self.frequency]
        if interval == 0:
            return None
        # Overdue completions move forward from today; early ones retain their date anchor.
        next_date = max(self.due_date, today or date.today()) + timedelta(days=interval)
        return replace(self, due_date=next_date, completed=False, id=uuid4().hex)


@dataclass
class Pet:
    """A pet and its task history."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)
    id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self):
        """Validate basic pet information."""
        self.name = require_text(self.name, "Pet name")
        self.species = require_text(self.species, "Species")

    def add_task(self, task: Task) -> None:
        """Attach a task while rejecting duplicate identifiers."""
        if any(existing.id == task.id for existing in self.tasks):
            raise ValueError("This task is already attached to the pet.")
        self.tasks.append(task)

    def update_task(self, task_id: str, **changes) -> Task:
        """Validate an edited pending task before replacing it."""
        allowed = {"description", "time", "due_date", "duration_minutes", "priority", "frequency"}
        if not set(changes) <= allowed:
            raise ValueError("Only task details can be edited.")
        for index, task in enumerate(self.tasks):
            if task.id == task_id:
                if task.completed:
                    raise ValueError("Completed tasks are kept as history.")
                updated = replace(task, **changes)
                self.tasks[index] = updated
                return updated
        raise ValueError("Task not found.")

    def mark_task_complete(self, task_id: str, today: date | None = None) -> Task | None:
        """Complete a task and attach its next occurrence exactly once."""
        for task in self.tasks:
            if task.id == task_id:
                next_task = task.mark_complete(today)
                if next_task is not None:
                    self.add_task(next_task)
                return next_task
        raise ValueError("Task not found.")


@dataclass
class Owner:
    """An owner with pets and an optional planning preference."""

    name: str
    pets: list[Pet] = field(default_factory=list)
    preferred_pet_id: str | None = None

    def __post_init__(self):
        """Validate the owner's name."""
        self.name = require_text(self.name, "Owner name")

    def add_pet(self, pet: Pet) -> None:
        """Add a distinct pet; names need not be unique."""
        if any(existing.id == pet.id for existing in self.pets):
            raise ValueError("This pet is already registered.")
        self.pets.append(pet)

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return tasks together with the pet each belongs to."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]


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
