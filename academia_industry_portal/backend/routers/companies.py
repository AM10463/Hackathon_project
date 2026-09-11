from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from database import get_session
from models.company import Company
from schemas.company import CompanyCreate, CompanyPublic
from security.auth import hash_password

router = APIRouter()


@router.post("/companies", response_model=CompanyPublic)
def create_company(
    company_data: CompanyCreate,
    session: Session = Depends(get_session),
):
    if session.exec(select(Company).where(Company.email == company_data.email)).first():
        raise HTTPException(status_code=409, detail="Company email already registered")
    company = Company(
        name=company_data.name,
        email=company_data.email,
        password_hash=hash_password(company_data.password),
        industry=company_data.industry,
        location=company_data.location,
        description=company_data.description,
    )
    session.add(company)
    session.commit()
    session.refresh(company)
    return company
