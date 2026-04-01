"""CLI demo script for PawPal+ backend verification."""

from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task


def print_schedule(tasks: list[Task], heading: str) -> None:
    """Print a readable schedule table for terminal demos."""
    print(f"\n{heading}")
    print("-" * len(heading))
    if not tasks:
        print("No tasks found.")
        return

    print("Time  | Pet      | Task                     | Freq   | Status")
    print("------|----------|--------------------------|--------|--------")
    for task in tasks:
        print(task)


def main() -> None:
    """Create sample data and demonstrate scheduling behaviors."""
    owner = Owner(name="Pari", email="pari@example.com")
    buddy = Pet(name="Buddy", species="Dog", age=3)
    luna = Pet(name="Luna", species="Cat", age=5)
    owner.add_pet(buddy)
    owner.add_pet(luna)

    today = date.today()
    buddy.add_task(Task("Evening walk", "18:00", "Buddy", "daily", due_date=today))
    buddy.add_task(Task("Morning walk", "07:30", "Buddy", "daily", due_date=today))
    buddy.add_task(Task("Medication", "09:00", "Buddy", "weekly", due_date=today))
    luna.add_task(Task("Breakfast feeding", "08:00", "Luna", "daily", due_date=today))
    luna.add_task(Task("Grooming", "09:00", "Luna", "once", due_date=today))

    scheduler = Scheduler(owner)

    print_schedule(scheduler.sort_by_time(scheduler.get_todays_tasks()), "Today's Schedule")

    print("\nConflict Warnings")
    print("-----------------")
    warnings = scheduler.conflict_warnings()
    if warnings:
        for warning in warnings:
            print(warning)
    else:
        print("No conflicts detected.")

    print_schedule(
        scheduler.sort_by_time(scheduler.filter_by_pet("Buddy")),
        "Buddy's Tasks",
    )

    walk_task = next(task for task in buddy.tasks if task.description == "Morning walk")
    created_task = scheduler.handle_recurrence(walk_task)
    if created_task:
        print(
            "\nRecurring task created:",
            created_task.description,
            "due",
            created_task.due_date,
        )


if __name__ == "__main__":
    main()
