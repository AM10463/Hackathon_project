from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from database import get_session
from models.internship import Internship
from models.student import Student
from schemas.student import StudentCreate, StudentPublic
from security.auth import hash_password
from security.auth import require_role
from services.matching import calculate_match
from services.skills import internship_skill_names, sync_student_skills

router = APIRouter()


@router.post("/students", response_model=StudentPublic)
def create_student(
    student_data: StudentCreate,
    session: Session = Depends(get_session),
):
    if session.exec(select(Student).where(Student.email == student_data.email)).first():
        raise HTTPException(status_code=409, detail="Student email already registered")
    student = Student(
        name=student_data.name,
        email=student_data.email,
        password_hash=hash_password(student_data.password),
        college=student_data.college,
        course=student_data.course,
        year=student_data.year,
        skills=student_data.skills,
    )
    session.add(student)
    session.commit()
    session.refresh(student)
    sync_student_skills(session, student.id, student.skills)
    session.commit()
    return student


@router.get("/students", response_model=list[StudentPublic])
def get_students(session: Session = Depends(get_session)):
    return session.exec(select(Student)).all()


@router.get("/students/me/recommendations")
def recommendations(
    session: Session = Depends(get_session),
    current_user=Depends(require_role("student")),
):
    student = current_user["user"]
    results = []
    for internship in session.exec(select(Internship)).all():
        required = ",".join(internship_skill_names(session, internship.id)) or internship.required_skills
        match = calculate_match(student.skills, required)
        results.append({"internship_id": internship.id, "title": internship.title, "match_score": match["score"]})
    return sorted(results, key=lambda item: item["match_score"], reverse=True)[:5]


@router.get("/students/me/skill-gaps")
def skill_gaps(
    session: Session = Depends(get_session),
    current_user=Depends(require_role("student")),
):
    student = current_user["user"]
    available = set()
    for internship in session.exec(select(Internship)).all():
        available.update(internship_skill_names(session, internship.id))
    own = {skill.strip().lower() for skill in student.skills.split(",") if skill.strip()}
    return {"missing_skills": sorted(available - own)}
