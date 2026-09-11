from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from database import get_session
from models.company import Company
from models.student import Student
from schemas.auth import CurrentUser, LoginRequest, Token
from schemas.company import CompanyCreate, CompanyPublic
from schemas.student import StudentCreate, StudentPublic
from security.auth import create_access_token, get_current_user, hash_password, verify_password
from services.skills import sync_student_skills

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/student/register", response_model=StudentPublic, status_code=201)
def register_student(data: StudentCreate, session: Session = Depends(get_session)):
	if session.exec(select(Student).where(Student.email == data.email)).first():
		raise HTTPException(status_code=409, detail="Student email already registered")
	student = Student(
		name=data.name, email=data.email, password_hash=hash_password(data.password),
		college=data.college, course=data.course, year=data.year, skills=data.skills,
	)
	session.add(student)
	session.commit()
	session.refresh(student)
	sync_student_skills(session, student.id, student.skills)
	session.commit()
	return student


@router.post("/company/register", response_model=CompanyPublic, status_code=201)
def register_company(data: CompanyCreate, session: Session = Depends(get_session)):
	if session.exec(select(Company).where(Company.email == data.email)).first():
		raise HTTPException(status_code=409, detail="Company email already registered")
	company = Company(
		name=data.name, email=data.email, password_hash=hash_password(data.password),
		industry=data.industry, location=data.location, description=data.description,
	)
	session.add(company)
	session.commit()
	session.refresh(company)
	return company


@router.post("/login", response_model=Token)
def login(data: LoginRequest, session: Session = Depends(get_session)):
	model = Student if data.role == "student" else Company
	user = session.exec(select(model).where(model.email == data.email)).first()
	if user is None or not verify_password(data.password, user.password_hash):
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email, password, or role")
	return Token(access_token=create_access_token(user.id, data.role))


@router.get("/me", response_model=CurrentUser)
def me(current_user=Depends(get_current_user)):
	return CurrentUser(id=current_user["id"], role=current_user["role"], email=current_user["email"])
