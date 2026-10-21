from datetime import date, time

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption(
    "Plan your pets' care for the day. Add your pets and their tasks, and PawPal+ "
    "builds a schedule that fits your time, starting with the most important tasks."
)

# Create the Owner once; Streamlit reruns this script on every interaction,
# so keeping it in session_state preserves its pets and preferences.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_minutes=60)

owner = st.session_state.owner


def parse_list(text: str) -> list[str]:
    """Split a comma-separated string into trimmed, non-empty items."""
    return [item.strip() for item in text.split(",") if item.strip()]


# --- Owner ---------------------------------------------------------------
st.subheader("1. About you")

# Keyed widgets with fixed defaults keep their own value across reruns;
# we copy that value onto the Owner each time.
owner.name = st.text_input("Your name", value="Jordan", key="owner_name")

col1, col2 = st.columns(2)
with col1:
    owner.available_minutes = int(
        st.number_input(
            "Time available today (minutes)",
            min_value=0,
            max_value=1440,
            value=60,
            key="available_minutes",
        )
    )
with col2:
    day_start = st.time_input("Start your day at", value=time(8, 0), key="day_start")

prefs_text = st.text_input(
    "Your preferences (comma-separated)",
    value="outdoor time",
    key="owner_prefs",
    help="Tag tasks with these and the schedule will point out the match.",
)
owner.preferences = set()
for pref in parse_list(prefs_text):
    owner.add_preference(pref)

st.divider()

# --- Pets ----------------------------------------------------------------
st.subheader("2. Your pets")

with st.form("add_pet", clear_on_submit=True):
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        pet_name = st.text_input("Pet name", placeholder="Mochi")
    with col2:
        species = st.selectbox("Species", ["dog", "cat", "other"])
    with col3:
        age = st.number_input("Age", min_value=0, max_value=40, value=1)
    needs_text = st.text_input(
        "Care needs (comma-separated)", placeholder="exercise, feeding, medication"
    )
    if st.form_submit_button("Add pet"):
        name = pet_name.strip()
        if not name:
            st.error("Give your pet a name.")
        elif any(p.name.lower() == name.lower() for p in owner.pets):
            st.error(f"You already have a pet named {name}.")
        else:
            pet = Pet(name=name, species=species, age=int(age))
            for need in parse_list(needs_text):
                pet.add_need(need)
            owner.add_pet(pet)

if owner.pets:
    st.table(
        [
            {
                "Name": p.name,
                "Species": p.species,
                "Age": p.age,
                "Needs": ", ".join(sorted(p.needs)) or "—",
                "Tasks": len(p.tasks),
            }
            for p in owner.pets
        ]
    )
else:
    st.info("No pets yet. Add one above.")

st.divider()

# --- Tasks ---------------------------------------------------------------
st.subheader("3. Care tasks")

if not owner.pets:
    st.info("Add a pet first, then you can give it tasks.")
else:
    pets_by_name = {p.name: p for p in owner.pets}
    pet = pets_by_name[st.selectbox("For which pet?", list(pets_by_name), key="task_pet")]

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        task_title = st.text_input("Task title", value="Morning walk", key="task_title")
    with col2:
        duration = int(
            st.number_input(
                "Duration (min)", min_value=1, max_value=240, value=20, key="task_duration"
            )
        )
    with col3:
        priority = st.selectbox(
            "Priority", ["low", "medium", "high"], index=2, key="task_priority"
        )

    tag_options = sorted(pet.needs | owner.preferences)
    tags = st.multiselect(
        "What does this task cover?",
        tag_options,
        key=f"task_tags_{pet.name}",
        help=f"Pick from {pet.name}'s needs and your preferences.",
    )
    notes = st.text_input("Notes (optional)", key="task_notes")

    if duration > owner.available_minutes:
        st.warning(
            f"This task takes {duration} min, but you only have "
            f"{owner.available_minutes} min today. It won't fit in the schedule."
        )

    if st.button("Add task"):
        if not task_title.strip():
            st.error("Give the task a title.")
        else:
            pet.add_task(
                Task(
                    title=task_title.strip(),
                    duration_minutes=duration,
                    priority=priority,
                    notes=notes.strip(),
                    tags=set(tags),
                )
            )

    all_tasks = [(p, t) for p in owner.pets for t in p.tasks]
    if all_tasks:
        st.table(
            [
                {
                    "Pet": p.name,
                    "Task": t.title,
                    "Minutes": t.duration_minutes,
                    "Priority": t.priority,
                    "Covers": ", ".join(sorted(t.tags)) or "—",
                    "Notes": t.notes or "—",
                }
                for p, t in all_tasks
            ]
        )
        total = sum(t.duration_minutes for _, t in all_tasks)
        if total > owner.available_minutes:
            st.warning(
                f"Your tasks add up to {total} min, but you only have "
                f"{owner.available_minutes} min today. Lower-priority tasks will be skipped."
            )
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

# --- Schedule ------------------------------------------------------------
st.subheader("4. Today's schedule")

if st.button("Generate schedule", type="primary"):
    all_tasks = [(p, t) for p in owner.pets for t in p.tasks]
    if not all_tasks:
        st.info("Add at least one task to build a schedule.")
    else:
        plan = Scheduler(day_start=day_start).create_daily_plan(owner, date.today())
        used = sum(t.duration_minutes for _, t in plan)

        col1, col2 = st.columns(2)
        col1.metric("Tasks scheduled", f"{len(plan)} of {len(all_tasks)}")
        col2.metric("Time used", f"{used} of {owner.available_minutes} min")

        if plan:
            st.table(
                [
                    {
                        "Time": f"{t.start_time:%H:%M}–{t._calculate_end_time():%H:%M}",
                        "Pet": p.name,
                        "Task": t.title,
                        "Priority": t.priority,
                        "Why": t.reason,
                    }
                    for p, t in plan
                ]
            )
        else:
            st.warning("None of your tasks fit in the time you have today.")

        skipped = [(p, t) for p, t in all_tasks if not t.is_scheduled()]
        if skipped:
            st.markdown("**Not scheduled today**")
            for p, t in skipped:
                st.write(f"- {p.name}: {t.title}. {t.reason}")
