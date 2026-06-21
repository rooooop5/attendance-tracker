from sqlalchemy import select, and_
from sqlalchemy.orm import Session
from datetime import date

import models
from schemas import ClassExtraRequest, ClassHeldUpdateRequest, ClassSubstituteRequest
from exceptions import AlreadyExistsException, NotFoundException, BadRequestException


def add_extra_class(target_date: date, request: ClassExtraRequest, session: Session):
    seen_periods = set()

    for period in request.periods:
        if period in seen_periods:
            raise BadRequestException(
                detail="periods are coinciding in the request",
            )
        seen_periods.add(period)

    paper_result = session.execute(
        select(models.Paper).where(models.Paper.id == request.paper),
    )

    paper = paper_result.scalars().first()

    if not paper:
        raise NotFoundException(detail="paper not found")

    existing_periods_result = session.execute(
        select(models.Attendance).where(
            and_(models.Attendance.date == target_date, models.Attendance.period.in_(request.periods)),
        )
    )

    existing_periods = existing_periods_result.scalars().all()

    if existing_periods:
        raise AlreadyExistsException(detail="period already occupied")

    extra_classes: list[models.Attendance] = []

    for period in request.periods:
        extra_class = models.Attendance(
            date=target_date,
            paper_id=paper.id,
            period=period,
            held=True,
            attended=True,
        )
        extra_classes.append(extra_class)

    session.add_all(extra_classes)
    session.commit()

    for extra_class in extra_classes:
        session.refresh(extra_class)

    return extra_classes


def update_class_held_status(
    target_date: date, period: int, paper_id: int, request: ClassHeldUpdateRequest, session: Session
):
    scheduled_class_result = session.execute(
        select(models.Attendance).where(
            and_(
                models.Attendance.date == target_date,
                models.Attendance.period == period,
                models.Attendance.paper_id == paper_id,
            ),
        ),
    )

    scheduled_class = scheduled_class_result.scalars().first()

    if not scheduled_class:
        raise NotFoundException(f"class not found at period {period}")

    if request.held:
        other_paper_same_period = (
            session.execute(
                select(models.Attendance).where(
                    and_(
                        models.Attendance.date == target_date,
                        models.Attendance.period == period,
                        models.Attendance.paper_id != paper_id,
                        models.Attendance.held == True,
                    )
                )
            )
            .scalars()
            .all()
        )
        for other_paper in other_paper_same_period:
            other_paper.held = False
            other_paper.attended = False
        session.add_all(other_paper_same_period)

    scheduled_class.held = request.held

    if scheduled_class.held:
        scheduled_class.attended = True
    else:
        scheduled_class.attended = False

    session.add(scheduled_class)
    session.commit()
    session.refresh(scheduled_class)

    return scheduled_class


def substitute_class(target_date: date, period: int, request: ClassSubstituteRequest, session: Session):
    scheduled_class_result = session.execute(
        select(models.Attendance).where(
            and_(
                models.Attendance.date == target_date,
                models.Attendance.period == period,
                models.Attendance.held == True,
            ),
        )
    )

    scheduled_class = scheduled_class_result.scalars().first()

    if not scheduled_class:
        raise NotFoundException(detail=f"no class found at period {period}")

    paper_result = session.execute(select(models.Paper).where(models.Paper.id == request.paper))

    paper = paper_result.scalars().first()

    if not paper:
        raise NotFoundException(detail="paper not found")

    if scheduled_class.paper_id == paper.id:
        raise AlreadyExistsException(detail="substitute paper is already scheduled for this period")

    scheduled_class.held = False
    scheduled_class.attended = False

    substitute_class = models.Attendance(date=target_date, paper_id=paper.id, period=period, held=True, attended=True)

    attendance_rows = [scheduled_class, substitute_class]

    session.add_all(attendance_rows)
    session.commit()

    for row in attendance_rows:
        session.refresh(row)

    return {"scheduled_class": scheduled_class, "actual_class": substitute_class}
