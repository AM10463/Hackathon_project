import os
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database import create_db, get_session
from routers import applications, auth, companies, internships, students
from services.analytics import platform_summary


app = FastAPI(title="Academia-Industry Collaboration Portal")

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend" / "Student_Portal"

allowed_origins = os.getenv("FRONTEND_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    create_db()


@app.get("/")
def home():
    return FileResponse(FRONTEND_DIR / "html", media_type="text/html")


@app.get("/analytics")
def analytics(session=Depends(get_session)):
    return platform_summary(session)


@app.get("/portal", include_in_schema=False)
def portal():
    return FileResponse(FRONTEND_DIR / "html", media_type="text/html")


@app.get("/css", include_in_schema=False)
def stylesheet():
    return FileResponse(FRONTEND_DIR / "css", media_type="text/css")


@app.get("/JavaScript", include_in_schema=False)
def javascript():
    return FileResponse(FRONTEND_DIR / "JavaScript", media_type="application/javascript")


app.include_router(students.router)
app.include_router(companies.router)
app.include_router(internships.router)
app.include_router(applications.router)
app.include_router(auth.router)

app.mount("/", StaticFiles(directory=FRONTEND_DIR), name="frontend")
