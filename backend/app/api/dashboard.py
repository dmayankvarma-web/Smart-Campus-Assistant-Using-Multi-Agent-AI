from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.api.auth import get_current_user
from app.db.models import Student, Faculty, Course, CourseRegistration, LeaveRequest, ClassroomBooking, Classroom

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/stats")
def get_dashboard_stats(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    role = user["role"]
    user_id = user["sub"]
    
    if role == "student":
        student = db.query(Student).filter(Student.student_id == user_id).first()
        attendance = float(student.attendance_pct) if student else 0.0
        
        enrolled_courses = db.query(CourseRegistration).filter(
            CourseRegistration.student_id == user_id,
            CourseRegistration.status == "enrolled"
        ).count()
        
        completed_courses = db.query(CourseRegistration).filter(
            CourseRegistration.student_id == user_id,
            CourseRegistration.status == "completed"
        ).count()
        
        pending_leaves = db.query(LeaveRequest).filter(
            LeaveRequest.student_id == user_id,
            LeaveRequest.status == "pending"
        ).count()
        
        return {
            "attendance": attendance,
            "enrolled_courses": enrolled_courses,
            "completed_courses": completed_courses,
            "pending_leaves": pending_leaves,
            "role": "student"
        }
    else:
        # Faculty
        courses_taught = db.query(Course).filter(Course.faculty_id == user_id).count()
        
        classroom_bookings = db.query(ClassroomBooking).filter(
            ClassroomBooking.booked_by == user_id
        ).count()
        
        faculty = db.query(Faculty).filter(Faculty.faculty_id == user_id).first()
        faculty_dept = faculty.department if faculty else ""
        
        pending_leaves_to_approve = db.query(LeaveRequest).join(Student).filter(
            Student.department == faculty_dept,
            LeaveRequest.status == "pending"
        ).count()
        
        total_classrooms = db.query(Classroom).count()
        
        return {
            "courses_taught": courses_taught,
            "classroom_bookings": classroom_bookings,
            "pending_leaves": pending_leaves_to_approve,
            "total_classrooms": total_classrooms,
            "role": "faculty"
        }
