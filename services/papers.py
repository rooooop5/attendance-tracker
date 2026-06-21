from sqlalchemy import select, func
from sqlalchemy.orm import Session

from exceptions import NotFoundException, AlreadyExistsException, BadRequestException
import models
from schemas import Paper


def post_papers(papers: list[Paper], session: Session):
    requested_paper_names = [paper.name.strip().upper() for paper in papers]

    if len(requested_paper_names) != len(set(requested_paper_names)):
        raise BadRequestException(detail="duplicate papers in the request")

    result = session.execute(
        select(models.Paper).where(
            func.upper(models.Paper.name).in_(
                requested_paper_names,
            ),
        ),
    )

    existing_papers = result.scalars().all()

    if existing_papers:
        raise AlreadyExistsException(detail="paper already exists, clashing with existing paper")

    database_papers = [models.Paper(name=paper.name.strip()) for paper in papers]

    session.add_all(database_papers)
    session.commit()

    for database_paper in database_papers:
        session.refresh(database_paper)

    return database_papers


def get_papers(session: Session):
    result = session.execute(select(models.Paper))

    db_papers = result.scalars().all()

    return db_papers


def get_paper_attendance(paper_id: int, session: Session):
    result = session.execute(select(models.Paper).where(models.Paper.id == paper_id))

    db_papers = result.scalars().first()

    if not db_papers:
        raise NotFoundException(detail="paper not found")

    return db_papers.attendance_entries
