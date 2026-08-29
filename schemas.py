from pydantic import BaseModel, ConfigDict
from enum import StrEnum
from datetime import date


class Day(StrEnum):
    MON = "MONDAY"
    TUE = "TUESDAY"
    WED = "WEDNESDAY"
    THU = "THURSDAY"
    FRI = "FRIDAY"
    SAT = "SATURDAY"
    SUN = "SUNDAY"


class Paper(BaseModel):
    name: str


class PaperResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class Class(BaseModel):
    paper: str
    periods: list[int]

class ClassExtraRequest(BaseModel):
    paper:int
    periods:list[int]

class ClassSubstituteRequest(BaseModel):
    paper: int 


class ClassSubstituteResponse(BaseModel):
    scheduled_class: AttendanceResponse
    actual_class: AttendanceResponse


class DaySchedule(BaseModel):
    classes: list[Class]


class TimeTableResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    day: Day
    paper: PaperResponse
    period: int


class AttendanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    date: date
    period: int
    held: bool
    attended: bool
    paper: PaperResponse


class DayAttendanceResponse(BaseModel):
    date: date
    entries: list[AttendanceResponse] | None


class AttendanceUpdateRequest(BaseModel):
    attended: bool


class ClassHeldUpdateRequest(BaseModel):
    held: bool


class PercentageResponse(BaseModel):
    percentage: float | None


class AttendancePercentageResponse(PercentageResponse):
    attended: int
    held: int
