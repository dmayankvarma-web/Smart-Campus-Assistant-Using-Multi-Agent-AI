from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import date, time
from typing import List, Optional
from app.core.db import get_db
from app.api.auth import get_current_user
from app.db.models import Student, Faculty, Course, Attendance, Result, LeaveRequest, Classroom, ClassroomBooking, CourseRegistration

router = APIRouter(prefix="/data", tags=["data"])

# --- Leave Pydantic Schema ---
class LeaveCreate(BaseModel):
    start_date: date
    end_date: date
    reason: str

class LeaveReview(BaseModel):
    leave_id: int
    status: str  # 'approved', 'rejected'
    comments: Optional[str] = None

# --- Booking Pydantic Schema ---
class BookingCreate(BaseModel):
    room_number: str
    date: date
    start_time: str # "HH:MM"
    end_time: str # "HH:MM"
    purpose: str

# 1. Attendance
@router.get("/attendance")
def get_attendance(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    role = user["role"]
    user_id = user["sub"]
    
    if role == "student":
        records = db.query(Attendance).filter(Attendance.student_id == user_id).all()
        return [{
            "attendance_id": r.attendance_id,
            "course_code": r.course_code,
            "date": r.date.isoformat(),
            "status": r.status
        } for r in records]
    else:
        # Faculty can only see attendance records for the courses they teach
        records = db.query(Attendance).join(Course).filter(Course.faculty_id == user_id).all()
        return [{
            "attendance_id": r.attendance_id,
            "student_id": r.student_id,
            "course_code": r.course_code,
            "date": r.date.isoformat(),
            "status": r.status
        } for r in records]

# 2. Courses
@router.get("/courses")
def get_courses(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    role = user["role"]
    user_id = user["sub"]
    
    if role == "student":
        # Enrolled courses
        registrations = db.query(CourseRegistration).filter(CourseRegistration.student_id == user_id).all()
        return [{
            "course_code": r.course_code,
            "course_name": r.course.course_name,
            "credits": r.course.credits,
            "instructor": r.course.instructor.name if r.course.instructor else "TBD",
            "status": r.status,
            "grade": r.grade
        } for r in registrations]
    else:
        # Faculty see courses they teach
        courses = db.query(Course).filter(Course.faculty_id == user_id).all()
        return [{
            "course_code": c.course_code,
            "course_name": c.course_name,
            "credits": c.credits,
            "department": c.department
        } for c in courses]

# 3. Leave Requests
@router.get("/leaves")
def get_leaves(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    role = user["role"]
    user_id = user["sub"]
    
    if role == "student":
        leaves = db.query(LeaveRequest).filter(LeaveRequest.student_id == user_id).all()
    else:
        # Faculty see leaves for students in their department
        faculty = db.query(Faculty).filter(Faculty.faculty_id == user_id).first()
        faculty_dept = faculty.department if faculty else ""
        leaves = db.query(LeaveRequest).join(Student).filter(Student.department == faculty_dept).all()
        
    return [{
        "leave_id": l.leave_id,
        "student_id": l.student_id,
        "student_name": l.student.name if l.student else "Unknown",
        "start_date": l.start_date.isoformat(),
        "end_date": l.end_date.isoformat(),
        "reason": l.reason,
        "status": l.status,
        "reviewed_by": l.reviewed_by,
        "review_comments": l.review_comments
    } for l in leaves]

@router.post("/leaves")
def create_leave(payload: LeaveCreate, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user["role"] != "student":
        raise HTTPException(status_code=403, detail="Only students can apply for leaves.")
        
    new_leave = LeaveRequest(
        student_id=user["sub"],
        start_date=payload.start_date,
        end_date=payload.end_date,
        reason=payload.reason,
        status="pending"
    )
    db.add(new_leave)
    db.commit()
    return {"success": True, "message": "Leave request submitted successfully."}

@router.post("/leaves/review")
def review_leave(payload: LeaveReview, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user["role"] != "faculty":
        raise HTTPException(status_code=403, detail="Only faculty can review leave requests.")
        
    leave = db.query(LeaveRequest).filter(LeaveRequest.leave_id == payload.leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found.")
        
    leave.status = payload.status
    leave.reviewed_by = user["sub"]
    leave.review_comments = payload.comments
    
    db.commit()
    return {"success": True, "message": f"Leave request status updated to {payload.status}."}

# 4. Faculty Information
@router.get("/faculty")
def get_faculty_info(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    faculty_list = db.query(Faculty).all()
    return [{
        "faculty_id": f.faculty_id,
        "name": f.name,
        "email": f.email,
        "department": f.department,
        "designation": f.designation,
        "office_room": f.office_room
    } for f in faculty_list]

# 5. Classrooms & Bookings
@router.get("/classrooms")
def get_classrooms_and_bookings(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    classrooms = db.query(Classroom).all()
    bookings = db.query(ClassroomBooking).all()
    
    rooms_data = [{
        "room_number": c.room_number,
        "building": c.building,
        "capacity": c.capacity,
        "has_projector": c.has_projector
    } for c in classrooms]
    
    bookings_data = [{
        "booking_id": b.booking_id,
        "room_number": b.room_number,
        "booked_by": b.booked_by,
        "faculty_name": b.faculty.name if b.faculty else "Unknown",
        "date": b.date.isoformat(),
        "start_time": b.start_time.strftime("%H:%M"),
        "end_time": b.end_time.strftime("%H:%M"),
        "purpose": b.purpose
    } for b in bookings]
    
    return {
        "classrooms": rooms_data,
        "bookings": bookings_data
    }

@router.post("/classrooms/book")
def book_classroom(payload: BookingCreate, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user["role"] != "faculty":
        raise HTTPException(status_code=403, detail="Only faculty members are allowed to book classrooms.")
        
    # Parse times
    try:
        sh, sm = map(int, payload.start_time.split(":"))
        eh, em = map(int, payload.end_time.split(":"))
        start_t = time(sh, sm)
        end_t = time(eh, em)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid time format. Use HH:MM.")
        
    # Check for room overlap
    overlap = db.query(ClassroomBooking).filter(
        ClassroomBooking.room_number == payload.room_number,
        ClassroomBooking.date == payload.date,
        ClassroomBooking.start_time < end_t,
        ClassroomBooking.end_time > start_t
    ).first()
    
    if overlap:
        raise HTTPException(status_code=400, detail="Classroom is already booked for this slot.")
        
    booking = ClassroomBooking(
        room_number=payload.room_number,
        booked_by=user["sub"],
        date=payload.date,
        start_time=start_t,
        end_time=end_t,
        purpose=payload.purpose
    )
    db.add(booking)
    db.commit()
    
    return {"success": True, "message": "Classroom booked successfully."}
