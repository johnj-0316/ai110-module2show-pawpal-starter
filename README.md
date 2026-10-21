# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## 🛠️ Implementation Summary

PawPal+ plans a pet owner's day of care tasks. The logic lives in `pawpal_system.py` and uses four classes (see `diagrams/uml.mmd`):

- **`Owner`**: the person doing the care, with their `available_minutes` for the day, their `preferences`, and their `pets`.
- **`Pet`**: an animal with a set of care `needs` and a list of `tasks`.
- **`Task`**: one care activity with a duration, a priority (low/medium/high), and `tags` linking it to the pet's needs or the owner's preferences. Scheduling fills in its `start_time` and `reason`.
- **`Scheduler`**: builds the plan. `create_daily_plan(owner, day)` gathers every pet's tasks and sorts them by priority. It places them one after another from 08:00 until the owner's time runs out, and explains why each task was scheduled or skipped.

An owner has pets, and each pet has tasks. The scheduler uses all three without owning them, and each run rebuilds the plan from scratch. `main.py` prints a two-pet demo schedule, and `tests/` checks task completion and adding tasks to a pet.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
08:00-08:05  Luna   Thyroid pill (5 min) [high]
Why: High priority; meets Luna's need: medication; fits in the time available, starting at 08:00.
Note: Hide in a treat
08:05-08:15  Mochi  Breakfast (10 min) [high]
Why: High priority; meets Mochi's need: feeding; fits in the time available, starting at 08:05.
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
============================= test session starts ==============================
platform darwin -- Python 3.14.6, pytest-9.1.1, pluggy-1.7.0
rootdir: .../ai110-module2show-pawpal-starter
configfile: pytest.ini
plugins: anyio-4.15.1
collected 2 items

tests/tests/test_pawpal.py ..                                            [100%]

============================== 2 passed in 0.01s ===============================
```

## 📐 Smarter Scheduling

The scheduler is greedy: it takes tasks in priority order and places each one right after the last, starting at 08:00, until the owner's available minutes run out.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler._sort_tasks()` | High -> medium -> low priority. Ties go to the shorter task, so more tasks fit in the day. |
| Filtering | `Scheduler._task_fits()`, `Scheduler._place_tasks()` | A task is skipped if it needs more minutes than are left. Skipped tasks stay unscheduled and get a reason, e.g. "Skipped: needs 25 min but only 0 min left in Jordan's day." |
| Conflict handling | `Scheduler.create_daily_plan()`, `Scheduler._place_tasks()` | All pets' tasks share one timeline, and each task starts when the previous one ends, so the owner is never double-booked. Tasks can't request a fixed time of day yet. |
| Recurring tasks | — | Not implemented. Tasks are planned for a single day; there is no daily/weekly repeat yet. |
| Explanations | `Scheduler._build_reason()`, `Task.tags` | Each scheduled task gets a reason with its priority, start time, and any of the pet's needs or owner's preferences that match the task's tags. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
