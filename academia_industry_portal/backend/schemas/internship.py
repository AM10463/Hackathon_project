from sqlmodel import SQLModel


class InternshipCreate(SQLModel):
    title: str
    description: str
    company_id: int
    location: str
    duration: str
    required_skills: str


class InternshipUpdate(SQLModel):
    title: str | None = None
    description: str | None = None
    location: str | None = None
    duration: str | None = None
    required_skills: str | None = None


class InternshipPublic(SQLModel):
    id: int
    title: str
    description: str
    company_id: int
    location: str
    duration: str
    required_skills: str
