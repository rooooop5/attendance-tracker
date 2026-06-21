from fastapi import APIRouter

from schemas import TimeTableResponse, DaySchedule, Day
from database import DatabaseSession

router = APIRouter(prefix="/timetable", tags=["timetable"])


from services.timetable import get_timetable, post_day_schedule


@router.post("/{weekday}", tags=["timetable"], response_model=list[TimeTableResponse])
def post_day_schedule_endpoint(weekday: Day, day_scedule: DaySchedule, session: DatabaseSession):
    return post_day_schedule(weekday, day_scedule, session)


@router.get("", tags=["timetable"], response_model=list[TimeTableResponse])
def get_timetable_endpoint(session: DatabaseSession):
    return get_timetable(session)
