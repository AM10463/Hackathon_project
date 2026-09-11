from sqlmodel import Session, select

from models.application import Application
from models.company import Company
from models.internship import Internship
from models.student import Student


def platform_summary(session: Session) -> dict[str, int]:
	return {
		"students": len(session.exec(select(Student)).all()),
		"companies": len(session.exec(select(Company)).all()),
		"internships": len(session.exec(select(Internship)).all()),
		"applications": len(session.exec(select(Application)).all()),
		"selections": len(session.exec(select(Application).where(Application.status == "Selected")).all()),
	}
