from sqlmodel import SQLModel, Field


class Internship(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    description: str
    company_id: int = Field(foreign_key="company.id", index=True)
    location: str
    duration: str
    required_skills: str = ""
