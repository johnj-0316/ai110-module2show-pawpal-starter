from datetime import date, datetime, time

import pytest

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


def test_scheduler_orders_tasks_by_priority():
    owner = Owner("Jordan", 60)
    pet = Pet("Mochi", "dog", 3)
    tasks = [
        Task("Brush", 10, "low"),
        Task("Play", 10, "medium"),
        Task("Medication", 10, "high"),
    ]

    schedule = Scheduler().create_schedule(owner, pet, tasks, date(2026, 10, 20))

    assert [task.title for task in schedule] == ["Medication", "Play", "Brush"]


def test_scheduler_orders_equal_priority_tasks_by_shortest_duration():
    owner = Owner("Jordan", 60)
    pet = Pet("Mochi", "dog", 3)
    tasks = [
        Task("Long walk", 30, "high"),
        Task("Breakfast", 10, "high"),
        Task("Medication", 5, "high"),
    ]

    schedule = Scheduler().create_schedule(owner, pet, tasks, date(2026, 10, 20))

    assert [task.title for task in schedule] == ["Medication", "Breakfast", "Long walk"]


def test_tasks_that_exactly_fill_available_time_are_all_scheduled():
    owner = Owner("Jordan", 30)
    pet = Pet("Mochi", "dog", 3)
    tasks = [Task("Breakfast", 10, "high"), Task("Walk", 20, "medium")]

    schedule = Scheduler().create_schedule(owner, pet, tasks, date(2026, 10, 20))

    assert schedule == tasks


def test_task_that_does_not_fit_is_skipped_with_reason():
    owner = Owner("Jordan", 20)
    pet = Pet("Mochi", "dog", 3)
    task = Task("Long walk", 21, "high")

    schedule = Scheduler().create_schedule(owner, pet, [task], date(2026, 10, 20))

    assert schedule == []
    assert task.start_time is None
    assert task.reason == "Skipped: needs 21 min but only 20 min left in Jordan's day."


def test_scheduler_assigns_consecutive_non_overlapping_time_slots():
    owner = Owner("Jordan", 60)
    pet = Pet("Mochi", "dog", 3)
    first = Task("Breakfast", 10, "high")
    second = Task("Walk", 20, "medium")

    schedule = Scheduler(day_start=time(8, 0)).create_schedule(
        owner, pet, [first, second], date(2026, 10, 20)
    )

    assert schedule == [first, second]
    assert first.start_time == datetime(2026, 10, 20, 8, 0)
    assert second.start_time == datetime(2026, 10, 20, 8, 10)


def test_daily_plan_is_empty_when_owner_has_no_pets():
    owner = Owner("Jordan", 60)

    assert Scheduler().create_daily_plan(owner, date(2026, 10, 20)) == []


def test_daily_plan_is_empty_when_pet_has_no_tasks():
    owner = Owner("Jordan", 60)
    owner.add_pet(Pet("Mochi", "dog", 3))

    assert Scheduler().create_daily_plan(owner, date(2026, 10, 20)) == []


def test_multiple_pets_share_one_schedule_timeline():
    owner = Owner("Jordan", 60)
    dog = Pet("Mochi", "dog", 3)
    cat = Pet("Luna", "cat", 5)
    dog.add_task(Task("Walk Mochi", 20, "high"))
    cat.add_task(Task("Feed Luna", 10, "medium"))
    owner.add_pet(dog)
    owner.add_pet(cat)

    plan = Scheduler().create_daily_plan(owner, date(2026, 10, 20))

    assert [(pet.name, task.title) for pet, task in plan] == [
        ("Mochi", "Walk Mochi"),
        ("Luna", "Feed Luna"),
    ]
    assert plan[0][1].start_time == datetime(2026, 10, 20, 8, 0)
    assert plan[1][1].start_time == datetime(2026, 10, 20, 8, 20)


def test_schedule_reason_mentions_matching_pet_need_and_owner_preference():
    owner = Owner("Jordan", 30, preferences={"morning"})
    pet = Pet("Mochi", "dog", 3, needs={"exercise"})
    task = Task("Morning walk", 20, "high", tags={"exercise", "morning"})

    Scheduler().create_schedule(owner, pet, [task], date(2026, 10, 20))

    assert "meets Mochi's need: exercise" in task.reason
    assert "matches Jordan's preference: morning" in task.reason


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"priority": "urgent"}, "priority must be one of"),
        ({"duration_minutes": 0}, "duration_minutes must be positive"),
        ({"frequency": "monthly"}, "frequency must be one of"),
    ],
)
def test_task_rejects_invalid_values(kwargs, message):
    values = {"title": "Task", "duration_minutes": 10, "priority": "medium"}
    values.update(kwargs)

    with pytest.raises(ValueError, match=message):
        Task(**values)
