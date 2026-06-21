from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase
from typing import Annotated
from fastapi import Depends


URL = "sqlite:///./attendance.db"


class Base(DeclarativeBase):
    pass


engine = create_engine(url=URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def get_database_session():
    with SessionLocal() as session:
        yield session


DatabaseSession = Annotated[Session, Depends(get_database_session)]