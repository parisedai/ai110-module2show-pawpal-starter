"""PawPal+ Streamlit UI integrated with backend logic."""

from datetime import date

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="", email="")
if "owner_set" not in st.session_state:
    st.session_state.owner_set = False
if "scheduler" not in st.session_state:
    st.session_state.scheduler = None

st.title("PawPal+ Smart Scheduler")
st.caption("Plan pet care tasks, sort by time, detect conflicts, and handle recurring tasks.")

with st.sidebar:
    st.header("Owner Setup")
    if not st.session_state.owner_set:
        owner_name = st.text_input("Owner name")
        owner_email = st.text_input("Owner email")
        if st.button("Save owner"):
            if owner_name.strip():
                st.session_state.owner = Owner(owner_name.strip(), owner_email.strip())
                st.session_state.scheduler = Scheduler(st.session_state.owner)
                st.session_state.owner_set = True
                st.rerun()
            else:
                st.warning("Owner name is required.")
    else:
        st.success(f"Signed in as {st.session_state.owner.name}")
        if st.button("Reset app"):
            for key in ["owner", "owner_set", "scheduler"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    st.divider()
    st.header("Add Pet")
    if st.session_state.owner_set:
        pet_name = st.text_input("Pet name")
        pet_species = st.selectbox("Species", ["Dog", "Cat", "Bird", "Rabbit", "Other"])
        pet_age = st.number_input("Age", min_value=0, max_value=30, value=1)
        if st.button("Add pet"):
            if not pet_name.strip():
                st.warning("Pet name is required.")
            elif pet_name.strip() in [pet.name for pet in st.session_state.owner.pets]:
                st.warning("That pet already exists.")
            else:
                st.session_state.owner.add_pet(Pet(pet_name.strip(), pet_species, int(pet_age)))
                st.success(f"Added {pet_name.strip()}.")
    else:
        st.info("Save owner details first.")

if not st.session_state.owner_set:
    st.info("Use the sidebar to save owner details and start scheduling.")
    st.stop()

owner = st.session_state.owner
scheduler = st.session_state.scheduler

schedule_tab, add_task_tab, pets_tab = st.tabs(["Today's Schedule", "Add Task", "My Pets"])

with add_task_tab:
    st.subheader("Schedule a Task")
    if not owner.pets:
        st.warning("Add at least one pet first.")
    else:
        pet_options = [pet.name for pet in owner.pets]
        selected_pet = st.selectbox("Pet", pet_options)
        description = st.text_input("Task description", placeholder="Morning walk")
        task_time = st.time_input("Time")
        frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])
        due_date = st.date_input("Due date", value=date.today())

        if st.button("Add task"):
            if description.strip():
                pet = next(pet for pet in owner.pets if pet.name == selected_pet)
                pet.add_task(
                    Task(
                        description=description.strip(),
                        time=task_time.strftime("%H:%M"),
                        pet_name=selected_pet,
                        frequency=frequency,
                        due_date=due_date,
                    )
                )
                st.success("Task added.")
                for warning in scheduler.conflict_warnings():
                    st.warning(warning)
            else:
                st.warning("Task description is required.")

with schedule_tab:
    st.subheader("Today's Schedule")
    todays_tasks = scheduler.sort_by_time(scheduler.get_todays_tasks())

    for warning in scheduler.conflict_warnings():
        st.warning(warning)

    if not todays_tasks:
        st.info("No tasks due today.")
    else:
        rows = [
            {
                "Time": task.time,
                "Pet": task.pet_name,
                "Task": task.description,
                "Frequency": task.frequency,
                "Status": "Done" if task.completed else "Pending",
            }
            for task in todays_tasks
        ]
        st.table(rows)

    st.divider()
    st.subheader("Mark Task Complete")
    pending = scheduler.sort_by_time(scheduler.filter_by_status(completed=False))
    if pending:
        labels = [f"{task.time} - {task.description} ({task.pet_name})" for task in pending]
        selected_label = st.selectbox("Pending tasks", labels)
        if st.button("Mark complete"):
            task = pending[labels.index(selected_label)]
            next_task = scheduler.handle_recurrence(task)
            if next_task is None:
                st.success("Task completed.")
            else:
                st.success(f"Task completed. Recurring copy created for {next_task.due_date}.")
            st.rerun()
    else:
        st.success("All tasks are complete.")

with pets_tab:
    st.subheader("Pet Roster")
    if not owner.pets:
        st.info("No pets added yet.")
    for pet in owner.pets:
        with st.expander(f"{pet.name} ({pet.species}, age {pet.age})"):
            pet_tasks = scheduler.sort_by_time(scheduler.filter_by_pet(pet.name))
            if pet_tasks:
                st.table(
                    [
                        {
                            "Time": task.time,
                            "Task": task.description,
                            "Frequency": task.frequency,
                            "Due": str(task.due_date),
                            "Status": "Done" if task.completed else "Pending",
                        }
                        for task in pet_tasks
                    ]
                )
            else:
                st.write("No tasks for this pet.")

            if st.button(f"Remove {pet.name}", key=f"remove_{pet.name}"):
                owner.remove_pet(pet.name)
                st.rerun()
