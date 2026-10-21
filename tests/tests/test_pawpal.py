from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete_changes_status():
    task = Task("Morning walk", 30, "high")
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet("Mochi", "dog", 3)
    assert len(pet.tasks) == 0

    pet.add_task(Task("Breakfast", 10, "high"))

    assert len(pet.tasks) == 1


def test_completing_daily_task_creates_next_day_occurrence():
    pet = Pet("Mochi", "dog", 3)
    walk = Task("Morning walk", 30, "high", frequency="daily", due_date=date(2026, 10, 20))
    pet.add_task(walk)

    next_walk = pet.complete_task(walk)

    assert walk.completed is True
    assert next_walk is not None
    assert next_walk.completed is False
    assert next_walk.due_date == date(2026, 10, 21)
    assert len(pet.tasks) == 2


def test_completing_weekly_task_creates_occurrence_a_week_later():
    bath = Task("Bath", 20, "medium", frequency="weekly", due_date=date(2026, 10, 20))

    assert bath.mark_complete().due_date == date(2026, 10, 27)


def test_completing_one_time_task_creates_nothing():
    pet = Pet("Mochi", "dog", 3)
    vet = Task("Vet visit", 60, "high")
    pet.add_task(vet)

    assert pet.complete_task(vet) is None
    assert len(pet.tasks) == 1


def test_scheduler_skips_occurrence_not_yet_due():
    owner = Owner("Jordan", 120)
    pet = Pet("Mochi", "dog", 3)
    owner.add_pet(pet)
    walk = Task("Morning walk", 30, "high", frequency="daily", due_date=date(2026, 10, 20))
    pet.add_task(walk)
    pet.complete_task(walk)

    today = Scheduler().create_daily_plan(owner, date(2026, 10, 20))
    tomorrow = Scheduler().create_daily_plan(owner, date(2026, 10, 21))

    assert today == []
    assert [t.due_date for _, t in tomorrow] == [date(2026, 10, 21)]
