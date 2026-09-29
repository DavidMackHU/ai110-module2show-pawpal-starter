"""Streamlit interface for the PawPal+ models."""
from datetime import date, datetime
import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler, PRIORITIES, FREQUENCIES, require_text
from main import demo_owner

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan")
owner = st.session_state.owner
scheduler = Scheduler(owner)


def notify(message):
    """Keep a notice visible after a UI refresh."""
    st.session_state.notice = message
    st.rerun()


def rows(tasks):
    """Format model objects for the schedule table."""
    return [{"Date": str(t.due_date), "Time": t.time, "Pet": p.name,
             "Task": t.description, "Minutes": t.duration_minutes,
             "Priority": t.priority.title(), "Repeats": t.frequency.title(),
             "Status": "✓ Complete" if t.completed else "Pending"} for p, t in tasks]


with st.sidebar:
    st.header("Your household")
    with st.form("owner_form"):
        name = st.text_input("Owner name", value=owner.name, key="owner_name")
        if st.form_submit_button("Save owner"):
            try:
                owner.name = require_text(name, "Owner name")
                notify("Owner saved.")
            except ValueError as error:
                st.error(str(error))
    with st.form("pet_form", clear_on_submit=True):
        pet_name = st.text_input("Pet name", key="pet_name")
        species = st.selectbox("Species", ["dog", "cat", "bird", "rabbit", "other"], key="species")
        if st.form_submit_button("Add pet"):
            try:
                owner.add_pet(Pet(pet_name, species))
                notify(f"Added {pet_name.strip()}.")
            except ValueError as error:
                st.error(str(error))
    for pet in owner.pets:
        st.write(f"🐾 {pet.name} · {pet.species}")
    if not owner.pets and st.button("Load sample household", key="load_demo"):
        st.session_state.owner = demo_owner(date.today())
        notify("Sample household loaded. Try the schedule and daily planner.")
    st.caption("Data stays during this browser session. Reloading the page or restarting the server may clear it.")

st.title("🐾 PawPal+")
st.write("A little structure. Happier pets. Plan care for your whole household.")
if "notice" in st.session_state:
    st.success(st.session_state.pop("notice"))
tasks = owner.get_all_tasks()
c1, c2, c3 = st.columns(3)
c1.metric("Pets", len(owner.pets))
c2.metric("Pending tasks", sum(not t.completed for _, t in tasks))
c3.metric("Completed", sum(t.completed for _, t in tasks))
if not owner.pets:
    st.info("Add your first pet in the sidebar, or load the sample household to explore.")
    st.stop()

pet_labels = {p.id: f"{p.name} ({p.species}) · {i + 1}" for i, p in enumerate(owner.pets)}
pet_by_id = {p.id: p for p in owner.pets}
schedule_tab, task_tab, plan_tab = st.tabs(["Schedule", "Add / edit tasks", "Daily planner"])

with task_tab:
    st.subheader("Add a care task")
    with st.form("task_form", clear_on_submit=True):
        pet_id = st.selectbox("Pet", list(pet_labels), format_func=pet_labels.get, key="task_pet")
        description = st.text_input("Task description", key="description")
        a, b, c = st.columns(3)
        due = a.date_input("Due date", key="due")
        at = b.time_input("Start time", value=datetime.strptime("08:00", "%H:%M").time(), key="at")
        duration = c.number_input("Duration (minutes)", 1, 1440, 20, key="duration")
        a, b = st.columns(2)
        priority = a.selectbox("Priority", list(PRIORITIES), index=1, key="priority")
        frequency = b.selectbox("Repeat", list(FREQUENCIES), key="frequency")
        if st.form_submit_button("Add task"):
            try:
                pet_by_id[pet_id].add_task(Task(description, at.strftime("%H:%M"), due,
                                               int(duration), priority, frequency))
                notify("Task added.")
            except ValueError as error:
                st.error(str(error))
    pending = scheduler.sort_by_time(completed=False)
    if pending:
        st.subheader("Edit a pending task")
        entries = {t.id: (p, t) for p, t in pending}
        edit_id = st.selectbox("Task to edit", list(entries), format_func=lambda k:
                              f"{entries[k][0].name} · {entries[k][1].description} · "
                              f"{entries[k][1].due_date} {entries[k][1].time}", key="edit_id")
        edit_pet, edit_task = entries[edit_id]
        with st.form(f"edit_{edit_id}"):
            edit_description = st.text_input("Description", edit_task.description)
            a, b, c = st.columns(3)
            edit_date = a.date_input("Date", edit_task.due_date)
            edit_time = b.time_input("Time", edit_task.start.time())
            edit_duration = c.number_input("Minutes", 1, 1440, edit_task.duration_minutes)
            a, b = st.columns(2)
            edit_priority = a.selectbox("Task priority", list(PRIORITIES), index=list(PRIORITIES).index(edit_task.priority))
            edit_frequency = b.selectbox("Recurrence", list(FREQUENCIES), index=list(FREQUENCIES).index(edit_task.frequency))
            if st.form_submit_button("Save changes"):
                try:
                    edit_pet.update_task(edit_id, description=edit_description, due_date=edit_date,
                                         time=edit_time.strftime("%H:%M"), duration_minutes=int(edit_duration),
                                         priority=edit_priority, frequency=edit_frequency)
                    notify("Task updated.")
                except ValueError as error:
                    st.error(str(error))

with schedule_tab:
    st.subheader("Your care schedule")
    a, b, c = st.columns(3)
    selected_date = a.date_input("Schedule date", key="schedule_date")
    pet_filter = b.selectbox("Filter by pet", [None] + list(pet_labels),
                            format_func=lambda v: "All pets" if v is None else pet_labels[v])
    status = c.selectbox("Status", ["All", "Pending", "Complete"])
    all_dates = st.checkbox("Show all dates", key="all_dates")
    day = None if all_dates else selected_date
    displayed = scheduler.sort_by_time(pet_id=pet_filter, day=day,
                                       completed={"All": None, "Pending": False, "Complete": True}[status])
    for warning in scheduler.detect_conflicts(day):
        st.warning(warning)
    st.caption("Conflict warnings cover the whole household, even when the table is filtered to one pet.")
    if displayed:
        st.dataframe(rows(displayed), hide_index=True, width="stretch")
    else:
        st.info("No tasks match these filters.")
    actionable = {t.id: (p, t) for p, t in displayed if not t.completed}
    if actionable:
        done_id = st.selectbox("Task to complete", list(actionable), format_func=lambda k:
                              f"{actionable[k][0].name} · {actionable[k][1].description} · "
                              f"{actionable[k][1].due_date} {actionable[k][1].time}")
        if st.button("Mark complete", key="complete"):
            pet, task = actionable[done_id]
            next_task = pet.mark_task_complete(done_id)
            message = "Task completed."
            if next_task:
                message += f" Next occurrence: {next_task.due_date} at {next_task.time}."
            notify(message)

with plan_tab:
    st.subheader("Make time for what matters")
    st.write("Choose a daily care budget. High priority tasks come first; your preferred pet breaks ties, followed by start time.")
    st.caption("Tasks keep their entered start times. The budget counts care minutes, not gaps between tasks. Skipped tasks remain pending.")
    a, b, c = st.columns(3)
    plan_date = a.date_input("Plan date", key="plan_date")
    budget = b.number_input("Available care minutes", 0, 1440, 60, key="budget")
    preference = c.selectbox("Preferred pet (tie breaker)", [None] + list(pet_labels),
                             format_func=lambda v: "No preference" if v is None else pet_labels[v])
    owner.preferred_pet_id = preference
    if st.button("Generate schedule", key="generate"):
        st.session_state.show_plan = True
    if st.session_state.get("show_plan"):
        chosen, skipped = scheduler.build_plan(plan_date, int(budget))
        used = sum(t.duration_minutes for _, t in chosen)
        st.success(f"{len(chosen)} tasks selected · {used} of {budget} minutes used")
        if chosen:
            st.dataframe(rows(chosen), hide_index=True, width="stretch")
            for pet, task in chosen:
                st.write(f"✓ {pet.name} / {task.description}: {task.priority} priority; fits the remaining budget and has no overlap with other selected tasks.")
        else:
            st.info("No pending tasks fit this date and budget.")
        if skipped:
            st.markdown("#### Tasks left out")
            for pet, task, reason in skipped:
                st.write(f"• {pet.name} / {task.description}: {reason}")
        for warning in scheduler.detect_conflicts(plan_date):
            st.warning(warning)
        st.caption("This is a suggested subset, not an automatic reschedule. Review skipped care tasks and adjust their times or your budget.")
