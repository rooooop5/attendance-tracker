from sqlalchemy import select, and_, func
from sqlalchemy.orm import Session
from datetime import date, timedelta

from schemas import Day, AttendanceUpdateRequest
import models
from exceptions import NotFoundException


def weekday_name(weekday: int):
    weekdays = [weekday.value for weekday in Day]
    return weekdays[weekday]


def mark_attendance(target_date: date, request: AttendanceUpdateRequest, session: Session, period=None):
    if period:
        attendance_rows_result = session.execute(
            select(models.Attendance).where(
                and_(
                    models.Attendance.date == target_date,
                    models.Attendance.period == period,
                    models.Attendance.held == True,
                )
            )
        )
    else:
        attendance_rows_result = session.execute(
            select(models.Attendance).where(
                and_(models.Attendance.date == target_date, models.Attendance.held == True),
            ),
        )

    attendance_rows: list[models.Attendance] = attendance_rows_result.scalars().all()

    if not attendance_rows:
        raise NotFoundException(f"attendance rows not found for {target_date}")

    for attendance_row in attendance_rows:
        attendance_row.attended = request.attended

    session.add_all(attendance_rows)
    session.commit()

    response = []

    for attendance_row in attendance_rows:
        session.refresh(attendance_row)
        response.append(attendance_row)

    return response


def create_attendance_for_date(target_date: date, timetable_rows: list[models.TimeTable], session: Session):
    attendance_entries: list[models.Attendance] = []

    existing_periods_result = session.execute(
        select(models.Attendance).where(
            models.Attendance.date == target_date,
        )
    )

    existing_periods_set = set(
        [attendance.period for attendance in existing_periods_result.scalars().all()],
    )

    for timetable_row in timetable_rows:
        timetable_row_dict: dict = timetable_row.to_dict_primitive_fields()

        if timetable_row.period in existing_periods_set:
            continue

        attendance_row = models.Attendance(date=target_date)

        for field, value in timetable_row_dict.items():
            if field == "id":
                continue
            setattr(attendance_row, field, value)

        attendance_entries.append(attendance_row)

    return attendance_entries


def generate_default_attendance_for_date(target_date: date, session: Session):
    target_date_weekday = weekday_name(target_date.weekday())

    timetable_rows_result = session.execute(select(models.TimeTable).where(models.TimeTable.day == target_date_weekday))
    timetable_rows: list[models.TimeTable] = timetable_rows_result.scalars().all()

    attendance_entries: list[models.Attendance] = create_attendance_for_date(target_date, timetable_rows, session)

    session.add_all(attendance_entries)
    session.commit()

    for entry in attendance_entries:
        session.refresh(entry)

    return attendance_entries


def backfill_attendance(session: Session):
    today = date.today()

    last_date_result = session.execute(select(func.max(models.Attendance.date)))

    last_date: date = last_date_result.scalars().first()

    if not last_date:
        last_date_result = session.execute(
            select(models.Settings).where(models.Settings.key == "SEM_START_DATE")
        ).scalar_one_or_none()

        if not last_date_result:
            raise NotFoundException("semester start date not found")

        last_date = date.fromisoformat(last_date_result.value)

    if not today > last_date:
        return []

    start_date = last_date + timedelta(days=1)

    missed_date = start_date

    attendance_entries = []

    while missed_date <= today:
        attendance_entries.append(
            {"date": missed_date, "entries": generate_default_attendance_for_date(missed_date, session)}
        )
        missed_date = missed_date + timedelta(days=1)

    return attendance_entries


def get_timetable_for_date(target_date: date, session: Session):
    result = session.execute(select(models.Attendance).where(models.Attendance.date == target_date))

    return result.scalars().all()
