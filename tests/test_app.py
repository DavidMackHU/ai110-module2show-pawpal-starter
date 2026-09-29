"""Exercise user workflows through Streamlit's native test runner."""
from pathlib import Path
from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "app.py"


def button(app, label):
    return next(item for item in app.button if item.label == label)


def test_add_pet_task_edit_complete_and_plan():
    app = AppTest.from_file(str(APP), default_timeout=60).run()
    assert not app.exception
    app.text_input(key="pet_name").set_value("Pip")
    button(app, "Add pet").click().run()
    assert len(app.session_state.owner.pets) == 1
    app.text_input(key="description").set_value("Breakfast")
    app.selectbox(key="frequency").set_value("daily")
    button(app, "Add task").click().run()
    assert not app.exception
    assert len(app.session_state.owner.pets[0].tasks) == 1
    next(item for item in app.text_input if item.label == "Description").set_value("Morning meal")
    button(app, "Save changes").click().run()
    assert app.session_state.owner.pets[0].tasks[0].description == "Morning meal"
    app.button(key="generate").click().run()
    assert any("1 tasks selected" in item.value for item in app.success)
    app.button(key="complete").click().run()
    pet = app.session_state.owner.pets[0]
    assert pet.tasks[0].completed and len(pet.tasks) == 2
    assert not app.exception
    assert any("0 tasks selected" in item.value for item in app.success)


def test_sample_household_and_invalid_inputs():
    app = AppTest.from_file(str(APP), default_timeout=60).run()
    button(app, "Add pet").click().run()
    assert app.error and not app.session_state.owner.pets
    app.button(key="load_demo").click().run()
    assert len(app.session_state.owner.pets) == 2
    assert app.warning
    app.number_input(key="budget").set_value(45)
    app.button(key="generate").click().run()
    assert any("45 of 45 minutes" in item.value for item in app.success)
    assert not app.exception
