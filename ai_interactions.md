# AI Interactions Log

## Agent Workflow

**Tool:** Codex in the project workspace, with terminal tools and the connected browser.

**Actual request:** "complete the assignment" after providing the PawPal+ assignment screenshot and starter README context.

**User's learning input:** "I learned how to us mermaid in real applications, the most difficult part was creating the components for the system, and i used AI as a tool to assist me in learning."

**Work completed by the agent:**

- Read the assignment and rubric in the browser and inspected the starter repository.
- Created `pawpal_system.py` with Owner, Pet, Task, and Scheduler.
- Created `main.py` with reproducible sorting, filters, recurrence, conflict warnings, priority sorting, and a 45-minute plan.
- Replaced the starter `app.py` with working forms, task editing/completion, filters, session state, and daily planning.
- Added the draft/final diagrams under `diagrams/`, `tests/test_pawpal.py`, `tests/test_app.py`, and `pytest.ini`.
- Updated `requirements.txt`, `.streamlit/config.toml`, `.gitignore`, README, and reflection.

**Additional algorithm:** `Scheduler.build_plan()` chooses a subset by priority, preferred pet, and available care minutes, prevents overlaps within that subset, and reports why tasks were skipped. It leaves stored tasks unchanged.

**Verification and corrections:**

The agent ran the CLI and the pytest suite. The first run passed 28 tests but one Streamlit workflow timed out during cold startup. The test startup timeout was increased from 15 to 60 seconds. Generated deprecated `use_container_width` arguments were changed to `width="stretch"`, and the Streamlit minimum version was raised. The next full run passed all 29 tests in 1.64 seconds. The final README contains captured CLI output.

**Manual corrections:** The student supplied the personal reflection input quoted above. No manual code corrections or personally rejected AI suggestion have been reported. Technical fixes described here were performed by the agent.

## Design decisions

- The four-class design keeps UI code out of the backend.
- Preferred pet IDs replaced the draft's broader species preference.
- Interval overlap checks handle different start times and midnight; adjacent tasks are allowed.
- Recurrences are created only once per completed occurrence.
- A readable greedy planner was used; no global-optimality claim is made.

## Prompt Comparison

No second model or separate prompting comparison was performed. This optional extension is not claimed.

## Git workflow

After the initial implementation was complete, the student requested six meaningful steps and control over each GitHub push. The completed version was preserved on the local `backup/pawpal-completed-before-six-steps` branch. The unpublished commits were then reorganized into design and skeletons, model behavior, scheduling and CLI, Streamlit UI, tests, and final documentation. The agent verified and committed each stage, then paused while the student pushed it. This history reflects a staged reconstruction of the completed implementation.
