from sqlmodel import SQLModel, Field
from sqlalchemy import UniqueConstraint


class Application(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student.id", index=True)
    internship_id: int = Field(foreign_key="internship.id", index=True)
    status: str = "Applied"

    __table_args__ = (
        UniqueConstraint("student_id", "internship_id", name="uq_student_internship"),
    )
