from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey, UniqueConstraint, Date, Boolean
from datetime import date
from database import Base


def serializer(obj):
    return {column.name: getattr(obj, column.name) for column in obj.__table__.columns}


class Paper(Base):
    __tablename__ = "papers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    attendance_entries: Mapped[list["Attendance"]] = relationship(back_populates="paper")

    def to_dict_primitive_fields(self):
        return serializer(self)


class TimeTable(Base):
    __tablename__ = "timetable"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    day: Mapped[str] = mapped_column(String(20), nullable=False)
    paper_id: Mapped[int] = mapped_column(Integer, ForeignKey("papers.id"), nullable=False, index=True)
    period: Mapped[int] = mapped_column(Integer, nullable=False)

    paper: Mapped["Paper"] = relationship()

    __table_args__ = (UniqueConstraint("day", "period", name="unique_timetable_entry"),)

    def to_dict_primitive_fields(self):
        return serializer(self)

    def to_dict_with_relantionship(self):
        data = serializer(self)
        data.update(
            {"paper": self.paper.to_dict_primitive_fields()},
        )
        return data


class Attendance(Base):
    __tablename__ = "attendance"
    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    paper_id: Mapped[int] = mapped_column(ForeignKey("papers.id"), nullable=False, index=True)
    period: Mapped[int] = mapped_column(Integer, nullable=False)
    held: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    attended: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    paper: Mapped["Paper"] = relationship(back_populates="attendance_entries")

    __table_args__ = (UniqueConstraint("date", "paper_id", "period", name="unique_attendance_entry"),)

    def to_dict_with_relationship(self):
        data = serializer(self)
        data.update(
            {"paper": self.paper.to_dict_primitive_fields()},
        )
        return data


class Settings(Base):
    __tablename__ = "settings"
    key: Mapped[str] = mapped_column(String, primary_key=True)
    value: Mapped[str] = mapped_column()
    value_type: Mapped[str] = mapped_column(default="string")

    __table_args__ = (UniqueConstraint("key", "value", name="unique_settings_entry"),)
