from datetime import date
from fastapi import APIRouter

from schemas import DayAttendanceResponse, AttendanceUpdateRequest, AttendanceResponse
from database import DatabaseSession
from services.attendance import (
    generate_default_attendance_for_date,
    mark_attendance,
    backfill_attendance,
    get_timetable_for_date,
)


router = APIRouter(prefix="/attendance", tags=["attendance"])


@router.post("/backfill", response_model=list[DayAttendanceResponse])
def backfill_attendance_endpoint(session: DatabaseSession):
    return backfill_attendance(session)


@router.post("/today", response_model=DayAttendanceResponse)
def generate_default_attendance_for_today_endpoint(session: DatabaseSession):
    return {
        "date": date.today(),
        "entries": generate_default_attendance_for_date(date.today(), session),
    }


@router.get("/today", response_model=list[AttendanceResponse])
def get_timetable_for_today_endpoint(session: DatabaseSession):
    return get_timetable_for_date(date.today(), session)


@router.patch("/today", response_model=DayAttendanceResponse)
def update_attendance_for_today_endpoint(request: AttendanceUpdateRequest, session: DatabaseSession):
    return {
        "date": date.today(),
        "entries": mark_attendance(date.today(), request, session),
    }


@router.patch("/today/{period}", response_model=DayAttendanceResponse)
def update_attendance_for_today_and_period_endpoint(period: int, request: AttendanceUpdateRequest, session: DatabaseSession):
    return {
        "date": date.today(),
        "entries": mark_attendance(date.today(), request, session, period=period),
    }


@router.get("/{target_date}", response_model=list[AttendanceResponse])
def get_timetable_for_date_endpoint(target_date: date, session: DatabaseSession):
    return get_timetable_for_date(target_date, session)


@router.post("/{target_date}", response_model=DayAttendanceResponse)
def generate_default_attendance_for_date_endpoint(target_date: date, session: DatabaseSession):
    return {
        "date": target_date,
        "entries": generate_default_attendance_for_date(target_date, session),
    }


@router.patch("/{target_date}", response_model=DayAttendanceResponse)
def update_attendance_for_date_endpoint(target_date: date, request: AttendanceUpdateRequest, session: DatabaseSession):
    return {
        "date": target_date,
        "entries": mark_attendance(target_date, request, session),
    }


@router.patch("/{target_date}/{period}", response_model=DayAttendanceResponse)
def update_attendance_for_date_and_period_endpoint(
    target_date: date, period: int, request: AttendanceUpdateRequest, session: DatabaseSession
):
    return {
        "date": target_date,
        "entries": mark_attendance(target_date, request, session, period=period),
    }
