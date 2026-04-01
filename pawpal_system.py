"""PawPal+ backend logic for pets, tasks, owners, and scheduling."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
import uuid


@dataclass
class Task:
    """Represents one pet-care task."""

    description: str
    time: str
    pet_name: str
    frequency: str = "once"
    due_date: date = field(default_factory=date.today)
    completed: bool = False
    task_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def next_occurrence(self) -> date:
        """Compute the next due date for recurring tasks."""
        if self.frequency == "daily":
            return self.due_date + timedelta(days=1)
        if self.frequency == "weekly":
            return self.due_date + timedelta(weeks=1)
        return self.due_date

    def __str__(self) -> str:
        status = "Done" if self.completed else "Pending"
        return (
            f"{self.time} | {self.pet_name:<8} | {self.description:<24} "
            f"| {self.frequency:<6} | {status}"
        )


@dataclass
class Pet:
    """Stores pet profile data and the pet's tasks."""

    name: str
    species: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet."""
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        """Remove a task by its id."""
        self.tasks = [task for task in self.tasks if task.task_id != task_id]


@dataclass
class Owner:
    """Represents an owner and their pets."""

    name: str
    email: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> None:
        """Remove a pet by name."""
        self.pets = [pet for pet in self.pets if pet.name != pet_name]

    def get_all_tasks(self) -> list[Task]:
        """Return all tasks across all pets."""
        return [task for pet in self.pets for task in pet.tasks]


class Scheduler:
    """Coordinates task retrieval, organization, and validation."""

    def __init__(self, owner: Owner) -> None:
        """Initialize scheduler with owner data source."""
        self.owner = owner

    def get_todays_tasks(self) -> list[Task]:
        """Get tasks due today."""
        today = date.today()
        return [task for task in self.owner.get_all_tasks() if task.due_date == today]

    def sort_by_time(self, tasks: list[Task] | None = None) -> list[Task]:
        """Sort tasks by HH:MM time string."""
        source = tasks if tasks is not None else self.owner.get_all_tasks()
        return sorted(source, key=lambda task: task.time)

    def filter_by_pet(self, pet_name: str) -> list[Task]:
        """Filter tasks to one pet."""
        return [task for task in self.owner.get_all_tasks() if task.pet_name == pet_name]

    def filter_by_status(self, completed: bool) -> list[Task]:
        """Filter tasks by completion state."""
        return [task for task in self.owner.get_all_tasks() if task.completed == completed]

    def handle_recurrence(self, task: Task) -> Task | None:
        """Complete a task and auto-create its next instance if recurring."""
        task.mark_complete()
        if task.frequency == "once":
            return None

        pet = next((pet for pet in self.owner.pets if pet.name == task.pet_name), None)
        if pet is None:
            return None

        next_task = Task(
            description=task.description,
            time=task.time,
            pet_name=task.pet_name,
            frequency=task.frequency,
            due_date=task.next_occurrence(),
        )
        pet.add_task(next_task)
        return next_task

    def detect_conflicts(self) -> list[tuple[Task, Task]]:
        """Return pairs of tasks with identical date and time."""
        conflicts: list[tuple[Task, Task]] = []
        seen_by_slot: dict[tuple[str, date], Task] = {}

        for task in self.owner.get_all_tasks():
            key = (task.time, task.due_date)
            if key in seen_by_slot:
                conflicts.append((seen_by_slot[key], task))
            else:
                seen_by_slot[key] = task

        return conflicts

    def conflict_warnings(self) -> list[str]:
        """Return readable warning lines for each conflict."""
        warnings: list[str] = []
        for first, second in self.detect_conflicts():
            warnings.append(
                f"Conflict at {first.time} on {first.due_date}: "
                f"{first.pet_name} - {first.description} vs "
                f"{second.pet_name} - {second.description}"
            )
        return warnings
