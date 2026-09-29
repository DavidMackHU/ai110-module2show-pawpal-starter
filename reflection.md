# PawPal+ Project Reflection

Personal learning statements below are based on my comments during this project. The technical sections were drafted with AI assistance from the implemented code and test results.

## 1. System Design

### a. Initial design

The three main user actions are adding pets, scheduling their care tasks, and viewing or completing tasks in a daily schedule. The design uses Owner, Pet, Task, and Scheduler. Owner keeps the household together; Pet owns its task history; Task represents a care occurrence; Scheduler organizes tasks across all pets. The draft diagram shows these relationships before the implementation details were filled in.

Creating the components of the system was the most difficult part for me. I learned how to use Mermaid in a real application to show how those components relate.

### b. Design changes

The initial draft included a preferred species field. The implementation replaced it with a preferred pet ID so the planner can favor one specific pet when priorities tie. Stable task and pet IDs also distinguish pets with the same name. The final UML adds task editing, priority sorting, and computed start/end times.

Completion has two responsibilities: Task changes its status and returns the next occurrence; Pet attaches that occurrence to its task list. This keeps recurrence out of the UI and prevents repeated completion from making duplicate future tasks.

## 2. Scheduling Logic and Tradeoffs

### a. Constraints and priorities

The scheduler considers due date, completion status, duration, priority, and the owner's preferred pet. It selects high priority tasks first, then uses pet preference and time to break ties. A task is selected only if it fits the remaining care minutes and does not overlap another selected task. The display then returns the chosen tasks to chronological order.

### b. Tradeoffs

The greedy plan is easy to explain but does not guarantee the most tasks or the best total score. A long high priority task may exclude several shorter tasks. This fits the goal of respecting explicitly assigned priorities while keeping the algorithm understandable.

The implementation checks full time intervals instead of only equal start times, so an 08:00 walk lasting 30 minutes conflicts with an 08:15 feeding. A daily plan only chooses tasks starting on that date; cross-midnight household warnings still need to be reviewed. Persistent storage and timezone handling are outside this prototype's scope.

## 3. AI Collaboration

### a. How AI was used

I used AI as a tool to assist me in learning. My request was to complete the assignment using the starter repository and the course requirements. The assistant read the requirements, proposed the four-class structure, implemented the backend and UI, created Mermaid diagrams, and ran the demo and tests. I supplied my personal learning points for this reflection.

The accepted implementation approach uses Python dataclasses for the models and keeps Streamlit separate from scheduling logic. This makes the same behavior available to the CLI demo, tests, and UI.

### b. Judgment and verification

I have not reported a specific AI suggestion that I personally rejected, so this reflection does not invent one. A revision made during the assisted build was replacing the draft's preferred-species field with a preferred-pet ID, which is more precise for a multi-pet household. Another correction updated the generated Streamlit table calls to the current `width="stretch"` API after a deprecation warning.

Correctness was checked through the CLI demonstration and pytest assertions about actual outcomes. One UI test initially timed out during cold startup; its startup allowance was increased and the full suite then passed. This was an execution-time issue rather than an assertion showing incorrect scheduling behavior.

This work used one conversation organized by development phase. Separate chat sessions were not used, so no benefit from separate sessions is claimed.

## 4. Testing and Verification

### a. What was tested

The 29 tests cover task management, sorting, filters, recurring dates and duplicate prevention, overlap warnings, priority and pet preferences, budget limits, invalid data, and editing. Calendar tests include leap years and year boundaries. UI tests add a pet and task, edit it, build a plan, complete a recurring task, and check sample data and validation.

These tests matter because a plausible-looking schedule could still lose a task, create duplicate recurrences, ignore a conflict, or exceed the owner's time budget. The CLI demonstrates two pets and four tasks and prints sorting, filtering, conflict warnings, a budgeted plan, and recurrence output.

### b. Confidence

The evidence supports a 4/5 confidence rating for a small classroom prototype. All 29 tests passed. More work should test large task histories, timezone changes, persistent storage, and multiple users. The greedy algorithm's limitations remain even when its tests pass.

## 5. Reflection

### a. What went well

I learned how to use Mermaid in a real application. The diagrams provide a way to connect the system components to the Python classes. AI supported my learning while helping turn the design into working code.

### b. What could improve

Creating the system components was the most difficult part for me. A useful next step would be to practice explaining each class's responsibility and tracing an action from the UI through the backend. For the application, saving data between runs and supporting owner availability windows would make it more useful.

### c. Key takeaway

My main takeaway is that AI can support learning while Mermaid makes the system structure visible. A working implementation also needs verification: a diagram explains the design, while examples and tests show whether the behavior matches it.
