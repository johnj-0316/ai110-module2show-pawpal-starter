"""PawPal+ core classes (based on diagrams/uml.mmd)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from typing import Optional

# Higher number = more important. Used for sorting and validation.
PRIORITY_RANK = {"low": 1, "medium": 2, "high": 3}


@dataclass
class Task:
    """A single pet care activity (walk, feeding, meds, etc.)."""

    title: str
    duration_minutes: int
    priority: str  # "low" | "medium" | "high"
    notes: str = ""
    tags: set[str] = field(default_factory=set)  # needs/preferences this task covers
    start_time: Optional[datetime] = None
    reason: Optional[str] = None
    completed: bool = False

    def __post_init__(self) -> None:
        self.priority = self.priority.lower().strip()
        if self.priority not in PRIORITY_RANK:
            raise ValueError(
                f"priority must be one of {list(PRIORITY_RANK)}, got {self.priority!r}"
            )
        if self.duration_minutes <= 0:
            raise ValueError("duration_minutes must be positive")
        # Normalize like Pet.needs / Owner.preferences so set matching works.
        self.tags = {t.strip().lower() for t in self.tags if t.strip()}

    def add_tag(self, tag: str) -> None:
        """Link this task to a need or preference (stored lowercase; blanks ignored)."""
        tag = tag.strip().lower()
        if tag:
            self.tags.add(tag)

    def mark_complete(self) -> None:
        """Record that this task has been done."""
        self.completed = True

    def is_scheduled(self) -> bool:
        """Return True if this task has been placed in the plan."""
        return self.start_time is not None

    def _calculate_end_time(self) -> datetime:
        """Return start_time + duration_minutes."""
        if self.start_time is None:
            raise ValueError(f"Task {self.title!r} has no start_time")
        return self.start_time + timedelta(minutes=self.duration_minutes)


@dataclass
class Pet:
    """A pet that needs care. Pet "1" o-- "0..*" Task."""

    name: str
    species: str
    age: int
    needs: set[str] = field(default_factory=set)
    tasks: list[Task] = field(default_factory=list)

    def add_need(self, need: str) -> None:
        """Add a care need for this pet (stored lowercase; blanks ignored)."""
        need = need.strip().lower()
        if need:
            self.needs.add(need)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        self.tasks.append(task)


@dataclass
class Owner:
    """The pet owner and their constraints. Owner "1" o-- "1..*" Pet."""

    name: str
    available_minutes: int
    preferences: set[str] = field(default_factory=set)
    pets: list[Pet] = field(default_factory=list)

    def add_preference(self, preference: str) -> None:
        """Add a scheduling preference (stored lowercase; blanks ignored)."""
        preference = preference.strip().lower()
        if preference:
            self.preferences.add(preference)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet with this owner."""
        self.pets.append(pet)


class Scheduler:
    """Builds a daily plan from an owner's constraints and their pets' tasks."""

    def __init__(self, day_start: time = time(8, 0)) -> None:
        self.day_start = day_start

    def create_schedule(
        self, owner: Owner, pet: Pet, tasks: list[Task], day: date
    ) -> list[Task]:
        """Return the tasks chosen and ordered for the given day.

        Tasks are placed back-to-back starting at ``day_start``, highest
        priority first, until the owner's available minutes run out.
        Tasks that don't fit are left unscheduled with a reason explaining why.
        """
        return [task for _, task in self._place_tasks(owner, [(pet, t) for t in tasks], day)]

    def create_daily_plan(self, owner: Owner, day: date) -> list[tuple[Pet, Task]]:
        """Schedule every task for all of the owner's pets in one shared timeline.

        Returns (pet, task) pairs in time order, so the owner is never
        double-booked and their available minutes are shared across pets.
        """
        pairs = [(pet, task) for pet in owner.pets for task in pet.tasks]
        return self._place_tasks(owner, pairs, day)

    def _place_tasks(
        self, owner: Owner, pairs: list[tuple[Pet, Task]], day: date
    ) -> list[tuple[Pet, Task]]:
        """Place tasks back-to-back by priority until the owner's time runs out."""
        pet_for = {id(task): pet for pet, task in pairs}

        # Clear results from any previous run so the plan is rebuilt fresh.
        for _, task in pairs:
            task.start_time = None
            task.reason = None

        current = datetime.combine(day, self.day_start)
        remaining = owner.available_minutes
        scheduled: list[tuple[Pet, Task]] = []

        for task in self._sort_tasks([task for _, task in pairs]):
            pet = pet_for[id(task)]
            if self._task_fits(task, remaining):
                task.start_time = current
                task.reason = self._build_reason(task, owner, pet)
                current = task._calculate_end_time()
                remaining -= task.duration_minutes
                scheduled.append((pet, task))
            else:
                task.reason = (
                    f"Skipped: needs {task.duration_minutes} min but only "
                    f"{remaining} min left in {owner.name}'s day."
                )

        return scheduled

    def _sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Order tasks by priority (high first), then shorter tasks first."""
        return sorted(
            tasks, key=lambda t: (-PRIORITY_RANK[t.priority], t.duration_minutes)
        )

    def _task_fits(self, task: Task, remaining_minutes: int) -> bool:
        """Return True if the task fits in the remaining time."""
        return task.duration_minutes <= remaining_minutes

    def _build_reason(self, task: Task, owner: Owner, pet: Pet) -> str:
        """Explain why this task was chosen and when it happens."""
        parts = [f"{task.priority.capitalize()} priority"]

        matched_needs = sorted(task.tags & pet.needs)
        if matched_needs:
            parts.append(f"meets {pet.name}'s need: {', '.join(matched_needs)}")

        matched_prefs = sorted(task.tags & owner.preferences)
        if matched_prefs:
            parts.append(f"matches {owner.name}'s preference: {', '.join(matched_prefs)}")

        start = task.start_time.strftime("%H:%M") if task.start_time else "?"
        parts.append(f"fits in the time available, starting at {start}")
        return "; ".join(parts) + "."
