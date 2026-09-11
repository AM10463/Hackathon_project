from pydantic import Field
from sqlmodel import SQLModel


class StudentCreate(SQLModel):
    name: str
    email: str
    password: str
    college: str
    course: str
    year: int = Field(ge=1, le=4)
    skills: str = ""


class StudentPublic(SQLModel):
    id: int
    name: str
    email: str
    college: str
    course: str
    year: int
    skills: str
