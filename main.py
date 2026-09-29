"""Deterministic CLI demonstration: python main.py."""

from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler


def demo_owner(day: date) -> Owner:
    """Create two pets with deliberately unsorted and conflicting tasks."""
    owner = Owner("Jordan")
    dog, cat = Pet("Biscuit", "dog"), Pet("Mochi", "cat")
    owner.add_pet(dog)
    owner.add_pet(cat)
    dog.add_task(Task("Evening walk", "18:00", day, 30, "medium", "daily"))
    dog.add_task(Task("Morning walk", "08:00", day, 30, "high", "daily"))
    cat.add_task(Task("Breakfast", "08:00", day, 10, "high", "daily"))
    cat.add_task(Task("Brush coat", "09:00", day, 15, "low", "weekly"))
    return owner


def print_tasks(tasks) -> None:
    """Print readable task rows instead of Python object representations."""
    for pet, task in tasks:
        status = "done" if task.completed else "pending"
        print(f"  {task.time} | {pet.name:7} | {task.description:13} | "
              f"{task.duration_minutes:2} min | {task.priority:6} | {status}")


def main() -> None:
    """Demonstrate sorting, filtering, planning, conflicts, and recurrence."""
    day = date(2026, 10, 1)
    owner = demo_owner(day)
    scheduler = Scheduler(owner)
    print(f"Today's Schedule (demo date: {day})")
    print_tasks(scheduler.sort_by_time(day=day))
    print("\nConflict warnings")
    for warning in scheduler.detect_conflicts(day):
        print(f"  {warning}")
    print("\nPriority order")
    print_tasks(scheduler.sort_by_priority(day=day))
    print("\nDaily plan: 45-minute budget")
    selected, skipped = scheduler.build_plan(day, 45)
    print_tasks(selected)
    for pet, task, reason in skipped:
        print(f"  Skipped {pet.name} / {task.description}: {reason}")
    print("\nMochi's pending tasks")
    print_tasks(scheduler.sort_by_time(pet_id=owner.pets[1].id, completed=False))
    dog = owner.pets[0]
    next_task = dog.mark_task_complete(dog.tasks[1].id, today=day)
    print(f"\nCompleted Morning walk; next occurrence: {next_task.due_date} {next_task.time}")
    print("Completed tasks")
    print_tasks(scheduler.sort_by_time(completed=True))


if __name__ == "__main__":
    main()
