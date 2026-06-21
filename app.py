from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import JSONResponse,FileResponse
from contextlib import asynccontextmanager
from datetime import date
from sqlalchemy import select

from database import Base, engine, DatabaseSession
from routers import attendance, classes, stats, papers, timetable
import scheduler
import models
from exceptions import DomainException, AlreadyExistsException

Base.metadata.create_all(bind=engine)

description = """This is an Attendance Management API for tracking daily college classes based on a timetable system.

The system is built around time slots (periods), where each period represents a scheduled class occurrence. Attendance is recorded per date and period, allowing flexible handling of real-world scenarios such as substitutions, cancellations, and extra classes.

Core features include:
- Generating daily attendance records automatically from a timetable
- Backfilling missing attendance data for previous dates
- Marking attendance per period or for an entire day
- Handling class substitutions, cancellations, and extra sessions
- Maintaining a historical record of attendance for analytics and statistics

The API is designed around a hybrid REST + action-based architecture to support both CRUD operations and domain-specific workflows."""


@asynccontextmanager
async def lifespan(_app: FastAPI):

    scheduler.backfill_attendance_task()
    scheduler.setup_bg_scheduler()
    yield
    scheduler.bg_scheduler.shutdown()


app = FastAPI(description=description, lifespan=lifespan)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(attendance.router)
app.include_router(classes.router)
app.include_router(stats.router)
app.include_router(papers.router)
app.include_router(timetable.router)


@app.get('/')
def home():
    return FileResponse('frontend/index.html')


@app.post("/settings/{sem_start_date}")
def post_sem_start_date_endpoint(sem_start_date: date, session: DatabaseSession):
    result = session.execute(select(models.Settings).where(models.Settings.key == "SEM_START_DATE"))

    existing_sem_start_date = result.scalars().first()

    if existing_sem_start_date:
        raise AlreadyExistsException(detail="the sem start date already exists")
    db_sem_start_date = models.Settings(key="SEM_START_DATE", value=sem_start_date.isoformat())
    session.add(db_sem_start_date)
    session.commit()
    session.refresh(db_sem_start_date)
    return db_sem_start_date


@app.exception_handler(DomainException)
def handler(request: Request, exception: DomainException):
    return JSONResponse(
        content={"detail": exception.detail, "path": request.url.path},
        status_code=DomainException.exception_to_status_map.get(exception.exception),
    )
