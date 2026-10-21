"""PawPal+ core classes (based on diagrams/uml.mmd)."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, datetime, time, timedelta
from typing import Optional

# Higher number = more important. Used for sorting and validation.
PRIORITY_RANK = {"low": 1, "medium": 2, "high": 3}

# Days until the next occurrence; "once" tasks don't repeat.
FREQUENCY_DAYS = {"once": None, "daily": 1, "weekly": 7}


def next_due_date(current: date, frequency: str) -> Optional[date]:
    """Return the next due date for a frequency, or None if it doesn't repeat."""
    days = FREQUENCY_DAYS[frequency]
    return current + timedelta(days=days) if days else None


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
    frequency: str = "once"  # "once" | "daily" | "weekly"
    due_date: Optional[date] = None  # None = due any day

    def __post_init__(self) -> None:
        """Validate priority, duration and frequency, and normalize tags."""
        self.priority = self.priority.lower().strip()
        if self.priority not in PRIORITY_RANK:
            raise ValueError(
                f"priority must be one of {list(PRIORITY_RANK)}, got {self.priority!r}"
            )
        if self.duration_minutes <= 0:
            raise ValueError("duration_minutes must be positive")
        self.frequency = self.frequency.lower().strip()
        if self.frequency not in FREQUENCY_DAYS:
            raise ValueError(
                f"frequency must be one of {list(FREQUENCY_DAYS)}, got {self.frequency!r}"
            )
        # Normalize like Pet.needs / Owner.preferences so set matching works.
        self.tags = set(filter(None, map(lambda t: t.strip().lower(), self.tags)))

    def add_tag(self, tag: str) -> None:
        """Link this task to a need or preference (stored lowercase; blanks ignored)."""
        tag = tag.strip().lower()
        if tag:
            self.tags.add(tag)

    def mark_complete(self) -> Optional[Task]:
        """Mark this task done and return its next occurrence if it repeats."""
        self.completed = True
        return self._next_occurrence()

    def is_recurring(self) -> bool:
        """Return True if this task repeats daily or weekly."""
        return FREQUENCY_DAYS[self.frequency] is not None

    def is_due(self, day: date) -> bool:
        """Return True if this task should be done on (or is overdue by) the given day."""
        return self.due_date is None or self.due_date <= day

    def _next_occurrence(self) -> Optional[Task]:
        """Build a fresh, incomplete copy of this task for its next due date."""
        if not self.is_recurring():
            return None
        due = next_due_date(self.due_date or date.today(), self.frequency)
        return replace(
            self,
            tags=set(self.tags),
            start_time=None,
            reason=None,
            completed=False,
            due_date=due,
        )

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

    def complete_task(self, task: Task) -> Optional[Task]:
        """Mark a task done and add its next occurrence to this pet, if any."""
        next_task = task.mark_complete()
        if next_task is not None:
            self.add_task(next_task)
        return next_task


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
        """Set the time of day the schedule starts."""
        self.day_start = day_start

    def create_schedule(
        self, owner: Owner, pet: Pet, tasks: list[Task], day: date
    ) -> list[Task]:
        """Schedule one pet's tasks and return the ones that fit, in time order."""
        return [task for _, task in self._place_tasks(owner, [(pet, t) for t in tasks], day)]

    def create_daily_plan(self, owner: Owner, day: date) -> list[tuple[Pet, Task]]:
        """Schedule all pets' tasks on one shared timeline as (pet, task) pairs."""
        pairs = [(pet, task) for pet in owner.pets for task in pet.tasks]
        return self._place_tasks(owner, pairs, day)

    def _place_tasks(
        self, owner: Owner, pairs: list[tuple[Pet, Task]], day: date
    ) -> list[tuple[Pet, Task]]:
        """Run filter → sort → fit → assign slot, and return the scheduled pairs."""
        pet_for = {id(task): pet for pet, task in pairs}
        tasks = [task for _, task in pairs]

        # Clear results from any previous run so the plan is rebuilt fresh.
        for task in tasks:
            task.start_time = None
            task.reason = None

        next_free = datetime.combine(day, self.day_start)
        remaining = owner.available_minutes
        scheduled: list[tuple[Pet, Task]] = []

        for task in self._sort_tasks(self._filter_tasks(tasks, day)):
            pet = pet_for[id(task)]
            if self._task_fits(task, remaining):
                next_free = self._assign_slot(task, next_free)
                remaining -= task.duration_minutes
                task.reason = self._build_reason(task, owner, pet)
                scheduled.append((pet, task))
            else:
                task.reason = self._build_skip_reason(task, remaining, owner)

        return scheduled

    def _filter_tasks(self, tasks: list[Task], day: date) -> list[Task]:
        """Keep tasks that are pending and due on the day; record why the rest are skipped."""
        ready: list[Task] = []
        for task in tasks:
            if task.completed:
                task.reason = "Skipped: already completed."
            elif not task.is_due(day):
                task.reason = f"Not due until {task.due_date:%a %b %d}."
            else:
                ready.append(task)
        return ready

    def _sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Order tasks by priority (high first), then shorter tasks first."""
        return sorted(
            tasks, key=lambda t: (-PRIORITY_RANK[t.priority], t.duration_minutes)
        )

    def _task_fits(self, task: Task, remaining_minutes: int) -> bool:
        """Return True if the task fits in the remaining time."""
        return task.duration_minutes <= remaining_minutes

    def _assign_slot(self, task: Task, next_free: datetime) -> datetime:
        """Start the task at the next free time and return when the timeline frees up again."""
        task.start_time = next_free
        return task._calculate_end_time()

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

    def _build_skip_reason(self, task: Task, remaining_minutes: int, owner: Owner) -> str:
        """Explain why a task didn't fit in the owner's remaining time."""
        return (
            f"Skipped: needs {task.duration_minutes} min but only "
            f"{remaining_minutes} min left in {owner.name}'s day."
        )
