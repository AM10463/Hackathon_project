from sqlmodel import SQLModel


class CompanyCreate(SQLModel):
    name: str
    email: str
    password: str
    industry: str
    location: str
    description: str = ""


class CompanyPublic(SQLModel):
    id: int
    name: str
    email: str
    industry: str
    location: str
    description: str
