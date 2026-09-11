from sqlmodel import SQLModel, Field


class Student(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str
    password_hash: str
    college: str
    course: str
    year: int
    skills: str = ""
