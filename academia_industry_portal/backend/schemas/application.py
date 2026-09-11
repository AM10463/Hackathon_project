from sqlmodel import SQLModel


class ApplicationCreate(SQLModel):
    student_id: int
    internship_id: int


class ApplicationPublic(SQLModel):
    id: int
    student_id: int
    internship_id: int
    status: str


class ApplicationStatusUpdate(SQLModel):
    status: str
