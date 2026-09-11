import os

from dotenv import load_dotenv
from sqlmodel import SQLModel, Session, create_engine
from models.application import Application
from models.company import Company
from models.internship import Internship
from models.student import Student
from models.skill import InternshipSkill, Skill, StudentSkill

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///database.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)


def create_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
        