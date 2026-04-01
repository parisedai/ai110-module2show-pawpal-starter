"""Pytest suite for PawPal+ core logic."""

from datetime import date, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


def make_owner_with_pets() -> tuple[Owner, Pet, Pet, Scheduler]:
    """Create reusable owner/pet fixtures."""
    owner = Owner(name="Test Owner", email="test@example.com")
    rex = Pet(name="Rex", species="Dog", age=2)
    miso = Pet(name="Miso", species="Cat", age=4)
    owner.add_pet(rex)
    owner.add_pet(miso)
    return owner, rex, miso, Scheduler(owner)


def test_task_mark_complete_changes_status() -> None:
    """Calling mark_complete should set completed to True."""
    task = Task(description="Walk", time="08:00", pet_name="Rex")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count() -> None:
    """Adding a task should increase task count for that pet."""
    _, rex, _, _ = make_owner_with_pets()
    before_count = len(rex.tasks)
    rex.add_task(Task(description="Fetch", time="10:00", pet_name="Rex"))
    assert len(rex.tasks) == before_count + 1


def test_sort_by_time_returns_chronological_order() -> None:
    """Scheduler should return tasks sorted by time ascending."""
    _, rex, _, scheduler = make_owner_with_pets()
    rex.add_task(Task("Evening walk", "18:00", "Rex"))
    rex.add_task(Task("Morning walk", "07:00", "Rex"))
    rex.add_task(Task("Noon meds", "12:00", "Rex"))

    sorted_tasks = scheduler.sort_by_time()
    assert [task.time for task in sorted_tasks] == ["07:00", "12:00", "18:00"]


def test_daily_recurrence_creates_tomorrows_task() -> None:
    """Completing a daily task should schedule the next day."""
    _, rex, _, scheduler = make_owner_with_pets()
    today = date.today()
    daily = Task("Morning walk", "07:00", "Rex", frequency="daily", due_date=today)
    rex.add_task(daily)

    next_task = scheduler.handle_recurrence(daily)
    assert next_task is not None
    assert next_task.due_date == today + timedelta(days=1)
    assert next_task.completed is False


def test_conflict_detection_flags_duplicate_times() -> None:
    """Two tasks in the same time slot should create one conflict pair."""
    _, rex, _, scheduler = make_owner_with_pets()
    today = date.today()
    rex.add_task(Task("Walk", "09:00", "Rex", due_date=today))
    rex.add_task(Task("Feed", "09:00", "Rex", due_date=today))

    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 1
