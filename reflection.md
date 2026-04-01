# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- I designed four main classes: `Owner`, `Pet`, `Task`, and `Scheduler`.
- `Owner` stores owner identity and a list of pets.
- `Pet` stores pet profile data and that pet's tasks.
- `Task` stores one care activity (description, time, frequency, due date, completion state).
- `Scheduler` is the coordination layer that reads tasks from owner/pet objects and applies sorting, filtering, recurrence handling, and conflict detection.

**b. Design changes**

- Yes. I added `due_date` and `task_id` fields to `Task` during implementation.
- `due_date` was needed for recurrence and for filtering today's tasks.
- `task_id` supports safer task removal and future editing without relying on non-unique descriptions.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- The scheduler currently considers task time (`HH:MM`), due date, frequency (`once`, `daily`, `weekly`), pet name, and completion status.
- I prioritized these because they are the minimum needed to build a useful daily plan and validate key scheduling behaviors before adding advanced optimization.

**b. Tradeoffs**

- The scheduler flags conflicts only when two tasks have the exact same date and time.
- It does not model overlap by duration yet.
- This tradeoff keeps the logic simple, readable, and testable for a module project while still providing immediate value to users.

---

## 3. AI Collaboration

**a. How you used AI**

- I used AI for class brainstorming, UML drafting, method skeleton generation, and test-case generation.
- The most useful prompts were specific implementation questions such as: "How should Scheduler retrieve tasks from Owner pets?" and "How should daily recurrence create the next due date safely?"

**b. Judgment and verification**

- I rejected an AI suggestion to overcomplicate conflict logic with duration overlap before duration was a core field in my data model.
- I kept exact-time conflict detection and verified correctness with focused pytest cases for duplicate and non-duplicate times.

---

## 4. Testing and Verification

**a. What you tested**

- I tested task completion status changes, pet task-count growth after add, sort order correctness, daily recurrence behavior, and conflict detection.
- These tests are important because they validate the core contracts between classes and catch regressions in the scheduler's key algorithms.

**b. Confidence**

- Confidence: 4/5.
- Next edge cases I would test are invalid time formats, empty owner/pet states in UI flows, weekly recurrence across month boundaries, and multi-conflict scenarios with three or more tasks at the same slot.

---

## 5. Reflection

**a. What went well**

- I am most satisfied with the clear class boundaries and how quickly that design translated into both CLI and Streamlit behavior.

**b. What you would improve**

- I would add task duration and priority weighting, then upgrade scheduler planning from simple sorting to a score-based planning method.

**c. Key takeaway**

- My key takeaway is that AI accelerates implementation best when I first define architecture and constraints clearly, then use tests as the final authority for correctness.
