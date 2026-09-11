from sqlmodel import Field, SQLModel


class Skill(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)


class StudentSkill(SQLModel, table=True):
    student_id: int = Field(foreign_key="student.id", primary_key=True)
    skill_id: int = Field(foreign_key="skill.id", primary_key=True)


class InternshipSkill(SQLModel, table=True):
    internship_id: int = Field(foreign_key="internship.id", primary_key=True)
    skill_id: int = Field(foreign_key="skill.id", primary_key=True)