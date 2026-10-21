"""PawPal+ core classes (skeleton based on diagrams/uml.mmd)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional


@dataclass
class Task:
    """A single pet care activity (walk, feeding, meds, etc.)."""

    title: str
    duration_minutes: int
    priority: str  # "low" | "medium" | "high"
    notes: str = ""
    start_time: Optional[datetime] = None
    reason: Optional[str] = None

    def is_scheduled(self) -> bool:
        """Return True if this task has been placed in the plan."""
        raise NotImplementedError

    def _calculate_end_time(self) -> datetime:
        """Return start_time + duration_minutes."""
        raise NotImplementedError


@dataclass
class Pet:
    """A pet that needs care. Pet "1" o-- "0..*" Task."""

    name: str
    species: str
    age: int
    needs: list[str] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)

    def add_need(self, need: str) -> None:
        """Add a care need for this pet."""
        raise NotImplementedError


@dataclass
class Owner:
    """The pet owner and their constraints. Owner "1" o-- "1..*" Pet."""

    name: str
    available_minutes: int
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def add_preference(self, preference: str) -> None:
        """Add a scheduling preference for this owner."""
        raise NotImplementedError


class Scheduler:
    """Builds a daily plan from an owner's constraints and a pet's tasks."""

    def create_schedule(
        self, owner: Owner, pet: Pet, tasks: list[Task], day: date
    ) -> list[Task]:
        """Return the tasks chosen and ordered for the given day."""
        raise NotImplementedError

    def _sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Order tasks by priority (and possibly duration)."""
        raise NotImplementedError

    def _task_fits(self, task: Task, remaining_minutes: int) -> bool:
        """Return True if the task fits in the remaining time."""
        raise NotImplementedError

    def _build_reason(self, task: Task, owner: Owner, pet: Pet) -> str:
        """Explain why this task was chosen and when it happens."""
        raise NotImplementedError
