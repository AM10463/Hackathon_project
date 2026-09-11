from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from database import get_session
from models.application import Application
from models.internship import Internship
from models.student import Student
from schemas.internship import InternshipCreate, InternshipPublic, InternshipUpdate
from security.auth import require_role
from services.matching import calculate_match
from services.skills import internship_skill_names, sync_internship_skills

router = APIRouter()


@router.post("/internships", response_model=InternshipPublic)
def create_internship(
    internship_data: InternshipCreate,
    session: Session = Depends(get_session),
    current_user=Depends(require_role("company")),
):
    if internship_data.company_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="You can only create internships for your company")
    internship = Internship(
        title=internship_data.title,
        description=internship_data.description,
        company_id=internship_data.company_id,
        location=internship_data.location,
        duration=internship_data.duration,
        required_skills=internship_data.required_skills,
    )
    session.add(internship)
    session.commit()
    session.refresh(internship)
    sync_internship_skills(session, internship.id, internship.required_skills)
    session.commit()
    return internship


@router.get("/internships", response_model=list[InternshipPublic])
def get_internships(session: Session = Depends(get_session)):
    return session.exec(select(Internship)).all()


@router.get("/internships/{internship_id}", response_model=InternshipPublic)
def get_internship(internship_id: int, session: Session = Depends(get_session)):
    internship = session.get(Internship, internship_id)
    if internship is None:
        raise HTTPException(status_code=404, detail="Internship not found")
    return internship


@router.put("/internships/{internship_id}", response_model=InternshipPublic)
def update_internship(
    internship_id: int,
    data: InternshipUpdate,
    session: Session = Depends(get_session),
    current_user=Depends(require_role("company")),
):
    internship = session.get(Internship, internship_id)
    if internship is None:
        raise HTTPException(status_code=404, detail="Internship not found")
    if internship.company_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="You do not own this internship")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(internship, key, value)
    session.add(internship)
    session.commit()
    session.refresh(internship)
    if data.required_skills is not None:
        sync_internship_skills(session, internship.id, internship.required_skills)
        session.commit()
    return internship


@router.delete("/internships/{internship_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_internship(
    internship_id: int,
    session: Session = Depends(get_session),
    current_user=Depends(require_role("company")),
):
    internship = session.get(Internship, internship_id)
    if internship is None:
        raise HTTPException(status_code=404, detail="Internship not found")
    if internship.company_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="You do not own this internship")
    session.delete(internship)
    session.commit()


@router.get("/students/{student_id}/internships/{internship_id}/match")
def get_skill_match(
    student_id: int,
    internship_id: int,
    session: Session = Depends(get_session),
):
    student = session.get(Student, student_id)
    internship = session.get(Internship, internship_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    if internship is None:
        raise HTTPException(status_code=404, detail="Internship not found")
    student_skills = student.skills
    required_skills = internship.required_skills
    normalized_student = ",".join(sorted(student_skills.split(",")))
    normalized_required = ",".join(sorted(internship_skill_names(session, internship.id)))
    result = calculate_match(normalized_student, normalized_required or required_skills)
    result["recommendation"] = "Excellent match" if result["score"] >= 80 else "Good match" if result["score"] >= 60 else "Needs skill development"
    return result


@router.get("/internships/{internship_id}/candidates")
def get_candidates(
    internship_id: int,
    session: Session = Depends(get_session),
    current_user=Depends(require_role("company")),
):
    internship = session.get(Internship, internship_id)
    if internship is None:
        raise HTTPException(status_code=404, detail="Internship not found")
    if internship.company_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="You do not own this internship")
    applications = session.exec(
        select(Application).where(Application.internship_id == internship_id)
    ).all()
    required = internship.required_skills
    return [
        {
            "student_id": application.student_id,
            "application_id": application.id,
            "status": application.status,
            "match": calculate_match(session.get(Student, application.student_id).skills, required),
        }
        for application in applications
    ]
