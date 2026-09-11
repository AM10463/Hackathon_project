from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from database import get_session
from models.application import Application
from models.internship import Internship
from models.student import Student
from schemas.application import ApplicationCreate, ApplicationPublic
from security.auth import require_role

router = APIRouter()


@router.post("/applications", response_model=ApplicationPublic)
def create_application(
    application_data: ApplicationCreate,
    session: Session = Depends(get_session),
    current_user=Depends(require_role("student")),
):
    if application_data.student_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="You can only apply as yourself")
    student = session.get(Student, application_data.student_id)
    internship = session.get(Internship, application_data.internship_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    if internship is None:
        raise HTTPException(status_code=404, detail="Internship not found")
    existing = session.exec(
        select(Application).where(
            Application.student_id == application_data.student_id,
            Application.internship_id == application_data.internship_id,
        )
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="You already applied to this internship")
    application = Application(
        student_id=application_data.student_id,
        internship_id=application_data.internship_id,
    )
    session.add(application)
    session.commit()
    session.refresh(application)
    return application


@router.get("/students/{student_id}/applications", response_model=list[ApplicationPublic])
def get_student_applications(student_id: int, session: Session = Depends(get_session), current_user=Depends(require_role("student"))):
    if student_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="You can only view your own applications")
    return session.exec(select(Application).where(Application.student_id == student_id)).all()


@router.get("/internships/{internship_id}/applications", response_model=list[ApplicationPublic])
def get_internship_applications(internship_id: int, session: Session = Depends(get_session), current_user=Depends(require_role("company"))):
    internship = session.get(Internship, internship_id)
    if internship is None:
        raise HTTPException(status_code=404, detail="Internship not found")
    if internship.company_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="You do not own this internship")
    return session.exec(select(Application).where(Application.internship_id == internship_id)).all()


@router.put("/applications/{application_id}/shortlist", response_model=ApplicationPublic)
def shortlist_application(application_id: int, session: Session = Depends(get_session), current_user=Depends(require_role("company"))):
    application = session.get(Application, application_id)
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    internship = session.get(Internship, application.internship_id)
    if internship.company_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="You do not own this application")
    if application.status != "Applied":
        raise HTTPException(status_code=400, detail="Only Applied applications can be shortlisted")
    application.status = "Shortlisted"
    session.add(application)
    session.commit()
    session.refresh(application)
    return application


@router.put("/applications/{application_id}/select", response_model=ApplicationPublic)
def select_application(application_id: int, session: Session = Depends(get_session), current_user=Depends(require_role("company"))):
    application = session.get(Application, application_id)
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    internship = session.get(Internship, application.internship_id)
    if internship.company_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="You do not own this application")
    if application.status != "Shortlisted":
        raise HTTPException(status_code=400, detail="Only Shortlisted applications can be selected")
    application.status = "Selected"
    session.add(application)
    session.commit()
    session.refresh(application)
    return application
