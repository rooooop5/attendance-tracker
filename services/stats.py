from sqlalchemy import select, func, and_
from sqlalchemy.orm import Session

import models


def get_total_attendance(session: Session, paper_id=None):
    if paper_id:
        total_attended_classes = session.execute(
            select(func.count(models.Attendance.id)).where(
                and_(
                    models.Attendance.held == True,
                    models.Attendance.attended == True,
                    models.Attendance.paper_id == paper_id,
                )
            )
        ).scalar()

        total_classes_held = session.execute(
            select(func.count(models.Attendance.id)).where(
                and_(models.Attendance.held == True, models.Attendance.paper_id == paper_id)
            )
        ).scalar()

    else:
        total_attended_classes = session.execute(
            select(func.count(models.Attendance.id)).where(
                and_(models.Attendance.held == True, models.Attendance.attended == True)
            )
        ).scalar()

        total_classes_held = session.execute(
            select(func.count(models.Attendance.id)).where(models.Attendance.held == True)
        ).scalar()

    if total_classes_held == 0:
        return {
            "attended": total_attended_classes,
            "held": total_classes_held,
            "percentage": None,
        }

    return {
        "attended": total_attended_classes,
        "held": total_classes_held,
        "percentage": total_attended_classes / total_classes_held,
    }
