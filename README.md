# Attendance Tracker

A small FastAPI attendance-management backend for tracking college classes, daily attendance, substitutions, cancellations, extra classes, and attendance statistics. The app also includes a simple HTML frontend in `frontend/index.html` for using the API from a browser.

## What It Does

- Stores papers/subjects.
- Stores a weekly timetable by day and period.
- Generates daily attendance rows from the timetable.
- Marks attendance for a full day or a single period.
- Supports cancelled classes through `held=False`.
- Supports class substitutions while preserving the original scheduled class as history.
- Supports extra classes outside the regular timetable.
- Computes overall and per-paper attendance percentages.
- Stores a semester start date for attendance backfill.

## Architecture

The backend is intentionally split into a few clear layers:

- `app.py` creates the FastAPI application, registers routers, handles domain exceptions, and sets up startup behavior.
- `routers/` contains HTTP route definitions and request/response wiring.
- `services/` contains the business logic for attendance, classes, papers, timetable, and stats.
- `models.py` contains SQLAlchemy ORM models.
- `schemas.py` contains Pydantic request and response schemas.
- `database.py` owns the SQLAlchemy engine/session dependency.
- `scheduler.py` contains background jobs for daily generation/backfill.
- `frontend/index.html` is a lightweight browser UI that talks to the API.

The main domain idea is:

```text
date + period = a timetable slot
date + period + paper = a concrete attendance record
held=True = the active class for that slot
```

That makes substitutions possible without deleting history. The original scheduled class can be marked `held=False`, and the substitute class can be inserted as the active row.

## Implementation Details

- The code separates HTTP routing from business logic, which keeps the routers readable.
- Domain exceptions such as `NotFoundException`, `AlreadyExistsException`, and `BadRequestException` make API failures more intentional.
- The substitution model preserves history instead of overwriting the original class.
- The held-status update flow enforces the important invariant that only one class should be active for a date and period.
- Paper lookup is case-insensitive, so names like `Math`, `MATH`, and `math` are treated as the same subject.
- The API exposes domain-friendly operations instead of forcing users to know internal database row IDs.
- The frontend exercises the main API workflows from one place.

## API Areas

- `/papers` creates and lists papers.
- `/timetable` creates and lists weekly timetable rows.
- `/attendance` generates, loads, backfills, and updates attendance.
- `/classes` adds extra classes, substitutes classes, and updates held/cancelled status.
- `/stats` returns overall and per-paper attendance statistics.
- `/settings/{sem_start_date}` stores the semester start date.

Interactive API docs are available at:

```text
http://localhost:8000/docs
```

## Running Locally

Install dependencies and run the API with `uv`:

```bash
uv run fastapi dev app.py
```

The API should be available at:

```text
http://localhost:8000
```

The frontend is a plain HTML file:

```text
frontend/index.html
```

Open it in a browser while the backend is running.

## Limitations

- There are no automated tests yet. 
- The scheduler assumes the app is running continuously.
- The frontend is intentionally simple and does not have a full state-management structure.
- Authentication and multi-user support are not implemented.
- The API is designed for local/personal use right now, not production deployment.

## Attribution

The HTML frontend and this README were written by Codex.
