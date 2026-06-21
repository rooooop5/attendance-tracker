from fastapi import APIRouter

from database import DatabaseSession
from schemas import PaperResponse, Paper, AttendanceResponse
from services.papers import get_paper_attendance, get_papers, post_papers

router = APIRouter(prefix="/papers", tags=["papers"])


@router.post("", tags=["papers"], response_model=list[PaperResponse])
def post_papers_endpoint(papers: list[Paper], session: DatabaseSession):
    return post_papers(papers, session)


@router.get("", response_model=list[PaperResponse], tags=["papers"])
def get_papers_endpoint(session: DatabaseSession):
    return get_papers(session)


@router.get("/{paper_id}/attendance", response_model=list[AttendanceResponse])
def get_paper_attendance_endpoint(paper_id: int, session: DatabaseSession):
    return get_paper_attendance(paper_id, session)
