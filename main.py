"""PawPal+ demo: build and print today's schedule for an owner with two pets."""

from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    owner = Owner(name="Jordan", available_minutes=90)
    owner.add_preference("outdoor time")
    owner.add_preference("quiet evening")

    mochi = Pet(name="Mochi", species="dog", age=3)
    mochi.add_need("exercise")
    mochi.add_need("feeding")

    luna = Pet(name="Luna", species="cat", age=7)
    luna.add_need("medication")
    luna.add_need("feeding")
    luna.add_need("enrichment")

    owner.add_pet(mochi)
    owner.add_pet(luna)

    mochi.add_task(Task("Morning walk", 30, "high", tags={"exercise", "outdoor time"}))
    mochi.add_task(Task("Breakfast", 10, "high", tags={"feeding"}))
    mochi.add_task(Task("Brush coat", 20, "low", notes="Use the slicker brush"))
    luna.add_task(Task("Thyroid pill", 5, "high", tags={"medication"}, notes="Hide in a treat"))
    luna.add_task(Task("Wet food", 10, "medium", tags={"feeding"}))
    luna.add_task(Task("Feather toy play", 15, "medium", tags={"enrichment"}))
    luna.add_task(Task("Litter box deep clean", 25, "low"))

    plan = Scheduler().create_daily_plan(owner, date.today())

    print(f"\nToday's Schedule for {owner.name} ({date.today():%A, %B %d})")
    print(f"Time available: {owner.available_minutes} min\n")
    for pet, task in plan:
        end = task._calculate_end_time()
        print(f"  {task.start_time:%H:%M}-{end:%H:%M}  {pet.name:<6} {task.title} "
              f"({task.duration_minutes} min) [{task.priority}]")
        print(f"               Why: {task.reason}")
        if task.notes:
            print(f"               Note: {task.notes}")

    used = sum(task.duration_minutes for _, task in plan)
    print(f"\nScheduled {len(plan)} tasks, {used} of {owner.available_minutes} min used.")

    skipped = [(pet, t) for pet in owner.pets for t in pet.tasks if not t.is_scheduled()]
    if skipped:
        print("\nNot scheduled today:")
        for pet, task in skipped:
            print(f"  {pet.name:<6} {task.title} - {task.reason}")
    print()


if __name__ == "__main__":
    main()
