# PawPal+

PawPal+ helps an owner organize care for multiple pets. Add pets and dated tasks, track completion, see conflicts, and choose a daily plan that fits a care-time budget.

## Run locally

Requires Python 3.10 or newer (tested with Python 3.12.10).

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe main.py
.venv\Scripts\python.exe -m streamlit run app.py
.venv\Scripts\python.exe -m pytest -q
```

On macOS/Linux, replace `.venv\Scripts\python.exe` with `.venv/bin/python`. If Python is installed as `py` on Windows, use `py -m venv .venv` for the first command. After activating a virtual environment, the equivalent commands are `python main.py`, `streamlit run app.py`, and `python -m pytest`.

Open the local URL printed by Streamlit. No API key or external AI service is needed to run this app.

## Features

- Multiple pets per owner, with stable IDs so pets can share a name.
- Add and edit tasks with dates, times, duration, priority, and recurrence.
- Chronological schedules filtered by date, pet, and completion status.
- Daily and weekly recurrence when a task is completed.
- Warnings for overlapping tasks, including across pets and midnight.
- Daily plans constrained by a care-time budget, task priority, and preferred pet.
- Reasons for selected and skipped tasks; planning does not silently change stored tasks.
- Session state retains the household during Streamlit reruns.

## System design

| Class | Responsibility |
| --- | --- |
| `Owner` | Stores the owner name, pets, and preferred pet; retrieves tasks across pets. |
| `Pet` | Stores identifying information and task history; adds, edits, and completes tasks. |
| `Task` | Represents one dated occurrence, validates input, computes its time interval, and creates its next recurrence. |
| `Scheduler` | Reads the owner's tasks, sorts and filters them, detects overlaps, and builds daily plans. |

The backend is in `pawpal_system.py` and does not import Streamlit. `main.py` demonstrates it from the terminal. `app.py` stores an `Owner` in `st.session_state` and calls the same backend methods.

UML sources: [initial draft](diagrams/uml_draft.mmd), [final design](diagrams/uml_final.mmd), and [grading entry point](diagrams/uml.mmd). The last two files contain the same final diagram. Open them in a Mermaid preview or paste their contents into [Mermaid Live Editor](https://mermaid.live/).

## Smarter Scheduling

| Feature | Method(s) | Behavior |
| --- | --- | --- |
| Chronological sorting | `Scheduler.sort_by_time()` | Sorts by actual date and 24-hour time, without changing stored order. |
| Priority sorting | `Scheduler.sort_by_priority()` | High, medium, low; chronological time breaks ties. |
| Filtering | `Scheduler.filter_tasks()` | Combines pet ID, completion status, and due date. |
| Conflict detection | `Scheduler.detect_conflicts()`, `overlaps()` | Compares pending task intervals across all pets. Adjacent intervals are allowed. Returns readable warnings. |
| Recurrence | `Task.mark_complete()`, `Pet.mark_task_complete()` | Preserves the completed occurrence and adds a new daily/weekly occurrence with a fresh ID. Repeated completion creates no duplicates. |
| Budgeted planning | `Scheduler.build_plan()` | Considers priority, preferred pet, then start time. Selects non-overlapping tasks that fit the remaining minutes and explains omissions. |

### Rules and tradeoffs

The plan uses a greedy algorithm: it chooses higher priority tasks first, rather than maximizing the total number of tasks or an overall score. Pet preference only breaks priority ties. Exact ties retain insertion order. Selected tasks are displayed chronologically.

Tasks keep their entered start times. The budget is total care minutes, not a continuous availability window. A plan considers pending tasks whose due date matches the requested day; it does not reserve time for tasks starting on another date. Household conflict warnings still report overlaps across midnight. Review those warnings before following a plan.

Recurring tasks are created upon completion, not expanded into an entire future calendar. The next date is `max(due_date, completion_date) + 1 or 7 days`. Completing an overdue task skips missed occurrences; completing early does not move the next occurrence before its original date. Completed records are kept as history and cannot be edited in the UI.

Sorting is O(n log n), filtering is O(n), and pairwise conflict checking and greedy overlap checks are O(n^2) in the worst case. This is reasonable for a small household.

## Sample Output

The demo uses a fixed date so it can be reproduced. Output captured from `python main.py`:

```text
Today's Schedule (demo date: 2026-10-01)
  08:00 | Biscuit | Morning walk  | 30 min | high   | pending
  08:00 | Mochi   | Breakfast     | 10 min | high   | pending
  09:00 | Mochi   | Brush coat    | 15 min | low    | pending
  18:00 | Biscuit | Evening walk  | 30 min | medium | pending

Conflict warnings
  Conflict: Biscuit / Morning walk (2026-10-01 08:00) overlaps Mochi / Breakfast (2026-10-01 08:00).

Priority order
  08:00 | Biscuit | Morning walk  | 30 min | high   | pending
  08:00 | Mochi   | Breakfast     | 10 min | high   | pending
  18:00 | Biscuit | Evening walk  | 30 min | medium | pending
  09:00 | Mochi   | Brush coat    | 15 min | low    | pending

Daily plan: 45-minute budget
  08:00 | Biscuit | Morning walk  | 30 min | high   | pending
  09:00 | Mochi   | Brush coat    | 15 min | low    | pending
  Skipped Mochi / Breakfast: Overlaps selected task: Morning walk.
  Skipped Biscuit / Evening walk: Needs 30 min; 15 min remain.

Mochi's pending tasks
  08:00 | Mochi   | Breakfast     | 10 min | high   | pending
  09:00 | Mochi   | Brush coat    | 15 min | low    | pending

Completed Morning walk; next occurrence: 2026-10-02 08:00
Completed tasks
  08:00 | Biscuit | Morning walk  | 30 min | high   | done
```

## Testing PawPal+

```powershell
python -m pytest -q
```

The suite tests task addition and completion, independent pet task lists, duplicate names/IDs, sorting, combined filters, daily/weekly recurrence, repeated completion, overdue/early completion, leap years, year boundaries, simultaneous and overnight conflicts, adjacent tasks, priority and preference rules, budget limits, empty data, validation, and atomic edits.

Streamlit AppTest also exercises adding a pet, adding and editing a recurring task, generating a plan, completing the task, sample loading, and invalid input. Test API reference: [Streamlit AppTest documentation](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest).

Successful run (Python 3.12.10, Streamlit 1.64.0, pytest 9.1.1):

```text
.............................                                            [100%]
29 passed in 1.64s
```

Confidence level: **4/5** for this classroom prototype, based on passing behavior and UI tests. It has no persistent database, multi-user synchronization, timezone support, notifications, or global optimization.

## Demo Walkthrough

1. Start Streamlit. Click **Load sample household**, or enter an owner name and add pets in the sidebar.
2. Open **Add / edit tasks**. Choose a pet, enter a description, date, start time, duration, priority, and recurrence, then click **Add task**. Existing pending tasks can be edited below the form.
3. Open **Schedule**. Tasks appear chronologically. Filter by pet and status, or select **Show all dates**. The sample contains an 08:00 overlap and displays a warning.
4. Open **Daily planner**, set **Available care minutes** to 45, and click **Generate schedule**. With no preference, the sample selects Biscuit's 30-minute morning walk and Mochi's 15-minute brushing. Breakfast conflicts with the walk, and the evening walk exceeds the remaining budget. Both omissions are explained.
5. Set the preferred pet to Mochi to see how a priority tie changes the chosen plan. The planner recomputes when inputs or tasks change after generation.
6. In **Schedule**, select a daily task and click **Mark complete**. Its completed record remains, and a new pending occurrence appears the next day. Use **Show all dates** to inspect it.
7. Try a blank description, a zero-minute budget, or an empty schedule. The app shows an error or empty-state message instead of crashing.

## UI and output formatting

`app.py` uses Streamlit tabs, forms, metrics, `st.dataframe`, `st.success`, `st.warning`, and `st.info`. Its `rows()` helper produces readable task tables and completion markers. `.streamlit/config.toml` sets a green theme. The CLI's `print_tasks()` uses aligned columns for time, pet, description, duration, priority, and status.

## Limits and future work

Data is held in memory for the browser session; a page reload or server restart can clear it. JSON persistence, reminders, flexible time windows, and a stronger optimization algorithm are possible future improvements. The app offers scheduling suggestions; skipped tasks remain pending and need the owner's attention.

## Project files

- `pawpal_system.py`: domain classes and scheduling algorithms
- `main.py`: reproducible demo and sample household
- `app.py`: Streamlit interface
- `tests/`: backend and UI behavior tests
- `diagrams/`: draft and final Mermaid diagrams
- `reflection.md`: design, tradeoffs, verification, and learning reflection
- `ai_interactions.md`: factual record of AI assistance
