from fastapi import APIRouter
from datetime import date

from schemas import (
    ClassExtraRequest,
    ClassSubstituteRequest,
    ClassHeldUpdateRequest,
    ClassSubstituteResponse,
    AttendanceResponse,
)
from database import DatabaseSession
from services.classes import add_extra_class, update_class_held_status, substitute_class

router = APIRouter(prefix="/classes", tags=["classes"])


@router.post("/today", response_model=list[AttendanceResponse])
def add_extra_class_for_today_endpoint(request: ClassExtraRequest, session: DatabaseSession):
    return add_extra_class(date.today(), request, session)


@router.patch("/today/{period}/papers/{paper_id}", response_model=AttendanceResponse)
def update_class_held_status_for_today_endpoint(
    paper_id: int, period: int, request: ClassHeldUpdateRequest, session: DatabaseSession
):
    return update_class_held_status(
        date.today(),
        period,
        paper_id,
        request,
        session,
    )


@router.post("/today/{period}/substitution", response_model=ClassSubstituteResponse)
def substitute_class_for_today_endpoint(period: int, request: ClassSubstituteRequest, session: DatabaseSession):
    return substitute_class(
        date.today(),
        period,
        request,
        session,
    )


@router.post("/{target_date}", response_model=list[AttendanceResponse])
def add_extra_class_endpoint(target_date: date, request: ClassExtraRequest, session: DatabaseSession):
    return add_extra_class(target_date, request, session)


@router.patch("/{target_date}/{period}/papers/{paper_id}", response_model=AttendanceResponse)
def update_class_held_status_for_date_endpoint(
    paper_id: int, target_date: date, period: int, request: ClassHeldUpdateRequest, session: DatabaseSession
):
    return update_class_held_status(
        target_date,
        period,
        paper_id,
        request,
        session,
    )


@router.post("/{target_date}/{period}/substitution", response_model=ClassSubstituteResponse)
def substitute_class_endpoint(
    target_date: date, period: int, request: ClassSubstituteRequest, session: DatabaseSession
):
    return substitute_class(target_date, period, request, session)
