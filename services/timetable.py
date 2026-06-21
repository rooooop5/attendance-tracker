from sqlalchemy import select, func, and_
from sqlalchemy.orm import Session

from schemas import DaySchedule, Day
import models
from exceptions import AlreadyExistsException, NotFoundException, BadRequestException


def post_day_schedule(weekday: Day, day_scedule: DaySchedule, session: Session):

    seen_periods = set()

    for class_info in day_scedule.classes:
        for period in class_info.periods:
            if period in seen_periods:
                raise BadRequestException(
                    detail="periods are coinciding in the request",
                )
            seen_periods.add(period)

    timetable_instance_list = []

    for class_info in day_scedule.classes:
        existing_class_result = session.execute(
            select(models.TimeTable).where(
                and_(
                    models.TimeTable.day == weekday,
                    models.TimeTable.period.in_(class_info.periods),
                ),
            ),
        )

        existing_class = existing_class_result.scalars().first()

        if existing_class is not None:
            raise AlreadyExistsException(detail=f"a class is already scheduled at the same time")

        result = session.execute(select(models.Paper).where(func.upper(models.Paper.name) == class_info.paper.upper().strip()))

        db_paper = result.scalars().first()

        if not db_paper:
            raise NotFoundException(detail=f"paper {class_info.paper} not found")

        for period in class_info.periods:
            timetable_instance = models.TimeTable(day=weekday, paper_id=db_paper.id, period=period)
            timetable_instance_list.append(timetable_instance)

    session.add_all(timetable_instance_list)
    session.commit()

    for timetable_instance in timetable_instance_list:
        session.refresh(timetable_instance)

    return timetable_instance_list


def get_timetable(session: Session):
    result = session.execute(select(models.TimeTable))

    timetable = result.scalars().all()

    return timetable
