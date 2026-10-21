# PawPal+ (Module 2 Project)

**PawPal+** is a Streamlit application that helps pet owners organize daily care
tasks across one or more pets.

## Overview

PawPal+ helps a busy owner stay consistent with pet care. It can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose each task

## What You Can Do

- Let a user enter basic owner + pet info
- Add care tasks with a duration, priority, notes, and matching tags
- Generate a daily schedule/plan based on constraints and priorities
- Review scheduled and skipped tasks with an explanation for each decision
- Preview the system from either the Streamlit UI or the command line

## Implementation Summary

PawPal+ plans a pet owner's day of care tasks. The logic lives in `pawpal_system.py` and uses four classes (see `diagrams/uml.mmd`):

- **`Owner`**: the person doing the care, with their `available_minutes` for the day, their `preferences`, and their `pets`.
- **`Pet`**: an animal with a set of care `needs` and a list of `tasks`.
- **`Task`**: one care activity with a duration, a priority (low/medium/high), and `tags` linking it to the pet's needs or the owner's preferences. Scheduling fills in its `start_time` and `reason`.
- **`Scheduler`**: builds the plan. `create_daily_plan(owner, day)` gathers every pet's tasks and sorts them by priority. It places them one after another from 08:00 until the owner's time runs out, and explains why each task was scheduled or skipped.

An owner has pets, and each pet has tasks. The scheduler uses all three without
owning them, and each run rebuilds the plan from scratch. `main.py` prints a
two-pet demo schedule, and `tests/` verifies the core scheduling and recurrence
behaviors.

## Features

- **Multi-pet planning:** Add multiple pets, record their care needs, and place
  all of their tasks on one shared daily timeline.
- **Priority-based sorting:** Tasks are sorted from high to medium to low
  priority. Tasks with the same priority are ordered by shortest duration first.
- **Due-date filtering:** Completed tasks and tasks that are not due yet are
  filtered out before scheduling.
- **Time-budget scheduling:** A greedy scheduling algorithm adds each eligible
  task only when it fits within the owner's remaining available minutes.
- **Conflict-free time slots:** Scheduled tasks start when the previous task
  ends. The Streamlit interface confirms conflict-free plans and warns if an
  overlap is detected.
- **Transparent decisions:** Every scheduled or skipped task receives an
  explanation based on priority, available time, pet needs, and owner
  preferences.
- **Recurring care:** Completing a daily or weekly task creates a fresh task for
  its next due date. One-time tasks do not recur.
- **Professional schedule display:** Streamlit tables summarize pets, entered
  tasks, the sorted daily plan, and tasks filtered out of the plan.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Run the Streamlit application:

```bash
streamlit run app.py
```

Run the command-line demonstration:

```bash
python main.py
```

## Testing PawPal+

```bash
python -m pytest
```

The tests cover task completion and recurrence, priority and duration sorting,
time-budget limits, consecutive non-overlapping schedule slots, multiple pets,
empty schedules, explanation text, and invalid task values.

Successful test output:

```text
============================= test session starts ==============================
platform darwin -- Python 3.14.6, pytest-9.0.3, pluggy-1.6.0
rootdir: /Users/johnmartin0227/Documents/Workspace/python/ai110-module2show-pawpal-starter
configfile: pytest.ini
plugins: anyio-4.12.1
collected 18 items

tests/tests/test_pawpal.py ..................                            [100%]

============================== 18 passed in 0.02s ==============================
```

**Confidence Level:** (4/5)

All currently tested behaviors pass. Confidence is four stars rather than five
because the Streamlit interface is not covered by automated tests and additional
real-world scheduling combinations could still reveal edge cases.

## Smarter Scheduling

Scheduler.create_daily_plan() builds the plan by filtering, sorting, and placing tasks in order, then explaining each decision.

Sorting: Scheduler._sort_tasks() orders tasks from high to medium to low priority.

Filtering: Scheduler._filter_tasks() skips tasks that are already done or not due yet. Scheduler._task_fits() then skips any task that needs more time than the owner has left.

Conflict handling: Scheduler._assign_slot() starts each task right after the previous one on a timeline shared by all pets. Conflicts aren't possible since tasks are added one after another, so detecting them isn't necessary.

Recurring tasks: Completing a daily or weekly task with Pet.complete_task() automatically creates its next occurrence through Task.mark_complete(). The next due date counts from the original due date, so a weekly Monday task stays on Mondays.

Explanations: Scheduler._build_reason() gives each scheduled task a reason based on its priority, start time, and any matching pet needs or owner preferences.

## Demo Walkthrough

1. Start the app with `streamlit run app.py`. Enter the owner's name, total
   minutes available for pet care, preferred start time, and optional scheduling
   preferences.
2. Add a pet with its name, species, age, and care needs. Add more pets if the
   owner needs one combined plan for several animals.
3. Select a pet and add care tasks. Each task includes a title, duration,
   priority, optional notes, and tags that can match the pet's needs or the
   owner's preferences. PawPal+ warns immediately when an individual task is
   longer than the owner's available time.
4. Review the task table. If the combined duration exceeds the time budget, the
   interface warns that lower-priority tasks may be skipped.
5. Select "generate schedule." The scheduler removes completed and not-yet-due
   tasks, sorts eligible tasks by priority and then duration, and assigns
   consecutive start times from the selected start of day.
6. Review today's schedule table. The app reports whether the timeline is free
   of conflicts and explains why each task was selected. Tasks that do not fit
   appear in a separate table with their skip reasons.

Example:

```text
Today's Schedule for Jordan (Tuesday, October 20)
Time available: 90 min

08:00-08:05  Luna   Thyroid pill (5 min) [high]
Why: High priority; meets Luna's need: medication; fits in the time available, starting at 08:00.
Note: Hide in a treat
08:05-08:15  Mochi  Breakfast (10 min) [high]
Why: High priority; meets Mochi's need: feeding; fits in the time available, starting at 08:05.
08:15-08:45  Mochi  Morning walk (30 min) [high]
Why: High priority; meets Mochi's need: exercise; matches Jordan's preference: outdoor time; fits in the time available, starting at 08:15.
08:45-08:55  Luna   Wet food (10 min) [medium]
Why: Medium priority; meets Luna's need: feeding; fits in the time available, starting at 08:45.
08:55-09:10  Luna   Feather toy play (15 min) [medium]
Why: Medium priority; meets Luna's need: enrichment; fits in the time available, starting at 08:55.
09:10-09:30  Mochi  Brush coat (20 min) [low]
Why: Low priority; fits in the time available, starting at 09:10.
Note: Use the slicker brush

Scheduled 6 tasks, 90 of 90 min used.

Not scheduled today:
  Luna   Litter box deep clean - Skipped: needs 25 min but only 0 min left in Jordan's day.
```
