from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.db import get_db
from app.core.security import create_access_token, verify_password
from app.db.models import Student, Faculty

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginRequest(BaseModel):
    user_id: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    name: str
    user_id: str

@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    # 1. Look up in students table
    student = db.query(Student).filter(Student.student_id == payload.user_id).first()
    if student and verify_password(payload.password, student.hashed_password):
        token = create_access_token(subject=student.student_id, role="student", name=student.name)
        return {
            "access_token": token,
            "token_type": "bearer",
            "role": "student",
            "name": student.name,
            "user_id": student.student_id
        }
        
    # 2. Look up in faculty table
    faculty = db.query(Faculty).filter(Faculty.faculty_id == payload.user_id).first()
    if faculty and verify_password(payload.password, faculty.hashed_password):
        token = create_access_token(subject=faculty.faculty_id, role="faculty", name=faculty.name)
        return {
            "access_token": token,
            "token_type": "bearer",
            "role": "faculty",
            "name": faculty.name,
            "user_id": faculty.faculty_id
        }
        
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect User ID or password",
    )

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import decode_access_token

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload

