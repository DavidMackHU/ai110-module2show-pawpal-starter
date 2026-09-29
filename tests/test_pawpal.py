"""Behavioral tests for pet care and scheduling edge cases."""
from datetime import date, timedelta
import pytest
from pawpal_system import Owner, Pet, Task, Scheduler

DAY = date(2026, 10, 1)


@pytest.fixture
def household():
    owner = Owner("Jordan")
    dog, cat = Pet("Biscuit", "dog"), Pet("Mochi", "cat")
    owner.add_pet(dog)
    owner.add_pet(cat)
    return owner, dog, cat, Scheduler(owner)


def task(description="Walk", at="08:00", **kwargs):
    return Task(description, at, due_date=kwargs.pop("due_date", DAY), **kwargs)


def test_addition_and_independent_lists(household):
    owner, dog, cat, _ = household
    activity = task()
    dog.add_task(activity)
    assert owner.get_all_tasks() == [(dog, activity)]
    assert cat.tasks == []
    with pytest.raises(ValueError):
        dog.add_task(activity)
    with pytest.raises(ValueError):
        owner.add_pet(dog)


def test_once_completion(household):
    _, dog, _, _ = household
    activity = task()
    dog.add_task(activity)
    assert dog.mark_task_complete(activity.id, DAY) is None
    assert activity.completed and len(dog.tasks) == 1


@pytest.mark.parametrize("frequency,days", [("daily", 1), ("weekly", 7)])
def test_recurrence_is_new_and_idempotent(household, frequency, days):
    _, dog, _, _ = household
    activity = task(frequency=frequency, priority="high")
    dog.add_task(activity)
    upcoming = dog.mark_task_complete(activity.id, DAY)
    assert upcoming.due_date == DAY + timedelta(days=days)
    assert upcoming.id != activity.id
    assert upcoming.priority == "high" and not upcoming.completed
    assert upcoming.time == activity.time
    assert dog.mark_task_complete(activity.id, DAY) is None
    assert len(dog.tasks) == 2


@pytest.mark.parametrize("day", [date(2026, 12, 31), date(2028, 2, 28)])
def test_recurrence_calendar_boundaries(day):
    assert task(due_date=day, frequency="daily").mark_complete(day).due_date == day + timedelta(days=1)


def test_overdue_and_early_completion_dates():
    assert task(due_date=DAY - timedelta(days=8), frequency="daily").mark_complete(DAY).due_date == DAY + timedelta(days=1)
    assert task(due_date=DAY + timedelta(days=8), frequency="weekly").mark_complete(DAY).due_date == DAY + timedelta(days=15)


def test_sorting_uses_date_and_time_without_mutation(household):
    _, dog, cat, scheduler = household
    late, early = task("Late", "18:00"), task("Early", "07:00")
    tomorrow = task(due_date=DAY + timedelta(days=1))
    dog.add_task(late)
    dog.add_task(early)
    cat.add_task(tomorrow)
    assert [t for _, t in scheduler.sort_by_time()] == [early, late, tomorrow]
    assert dog.tasks == [late, early]


def test_filters_and_duplicate_names(household):
    _, dog, cat, scheduler = household
    cat.name = dog.name
    dog.add_task(task(completed=True))
    cat.add_task(task())
    assert scheduler.filter_tasks(pet_id=dog.id, completed=False) == []
    assert len(scheduler.filter_tasks(pet_id=cat.id, completed=False, day=DAY)) == 1
    assert scheduler.filter_tasks(day=DAY + timedelta(days=1)) == []


def test_conflicts_and_adjacent_times(household):
    _, dog, cat, scheduler = household
    dog.add_task(task("Walk", "08:00", duration_minutes=30))
    cat.add_task(task("Food", "08:00", duration_minutes=10))
    cat.add_task(task("Brush", "08:30", duration_minutes=10))
    assert len(scheduler.detect_conflicts(DAY)) == 1
    cat.tasks[0].completed = True
    assert scheduler.detect_conflicts(DAY) == []


def test_overnight_overlap(household):
    _, dog, cat, scheduler = household
    dog.add_task(task("Night walk", "23:50", duration_minutes=30))
    cat.add_task(task("Food", "00:05", due_date=DAY + timedelta(days=1)))
    assert len(scheduler.detect_conflicts(DAY + timedelta(days=1))) == 1
    assert scheduler.detect_conflicts(DAY) == []


def test_plan_budget_priority_overlap_and_reasons(household):
    _, dog, cat, scheduler = household
    low = task("Long play", "07:00", duration_minutes=60, priority="low")
    high = task("Walk", "08:00", duration_minutes=30, priority="high")
    conflict = task("Brush", "08:15", priority="medium")
    short = task("Food", "09:00", duration_minutes=10, priority="low")
    for pet, activity in [(dog, low), (dog, high), (cat, conflict), (cat, short)]:
        pet.add_task(activity)
    selected, skipped = scheduler.build_plan(DAY, 40)
    assert [t for _, t in selected] == [high, short]
    assert {t.description for _, t, _ in skipped} == {"Long play", "Brush"}
    assert any("Overlaps" in reason for _, _, reason in skipped)
    assert any("remain" in reason for _, _, reason in skipped)
    assert not any(t.completed for _, t in scheduler.filter_tasks())


def test_preference_breaks_priority_tie(household):
    owner, dog, cat, scheduler = household
    dog.add_task(task(priority="high"))
    cat.add_task(task(priority="high"))
    owner.preferred_pet_id = cat.id
    assert scheduler.build_plan(DAY, 20)[0][0][0] is cat
    dog.tasks[0].priority = "low"
    owner.preferred_pet_id = dog.id
    assert scheduler.build_plan(DAY, 20)[0][0][0] is cat


def test_priority_sort_empty_and_zero_budget(household):
    _, dog, _, scheduler = household
    assert scheduler.build_plan(DAY, 0) == ([], [])
    assert scheduler.detect_conflicts() == []
    dog.add_task(task("Low", "06:00", priority="low"))
    dog.add_task(task("High", "10:00", priority="high"))
    assert scheduler.sort_by_priority()[0][1].description == "High"
    assert scheduler.build_plan(DAY, 0)[0] == []
    with pytest.raises(ValueError):
        scheduler.build_plan(DAY, -1)


def test_edit_validates_before_mutating(household):
    _, dog, _, _ = household
    activity = task()
    dog.add_task(activity)
    with pytest.raises(ValueError):
        dog.update_task(activity.id, duration_minutes=0)
    assert dog.tasks[0] is activity
    changed = dog.update_task(activity.id, description="New walk", time="10:00")
    assert changed.id == activity.id and changed.time == "10:00"
    dog.mark_task_complete(changed.id, DAY)
    with pytest.raises(ValueError):
        dog.update_task(changed.id, description="No")
    with pytest.raises(ValueError):
        dog.mark_task_complete("missing")


@pytest.mark.parametrize("changes", [
    {"description": " "}, {"time": "8:00"}, {"time": "24:00"}, {"time": "09:60"},
    {"duration_minutes": 0}, {"duration_minutes": -2}, {"duration_minutes": 1.5},
    {"duration_minutes": True}, {"priority": "urgent"}, {"frequency": "monthly"},
    {"due_date": "2026-10-01"},
])
def test_invalid_task_input(changes):
    with pytest.raises(ValueError):
        Task(**{"description": "Walk", **changes})


def test_blank_owner_and_pet():
    with pytest.raises(ValueError):
        Owner(" ")
    with pytest.raises(ValueError):
        Pet("", "dog")
