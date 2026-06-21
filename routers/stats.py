from fastapi import APIRouter
from database import DatabaseSession

from services.stats import get_total_attendance
from schemas import AttendancePercentageResponse

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/attendance", response_model=AttendancePercentageResponse)
def get_total_attendance_endpoint(session: DatabaseSession):
    return get_total_attendance(session)


@router.get("/attendance/{paper_id}", response_model=AttendancePercentageResponse)
def get_total_attendance_for_paper_endpoint(paper_id: int, session: DatabaseSession):
    return get_total_attendance(session, paper_id)
