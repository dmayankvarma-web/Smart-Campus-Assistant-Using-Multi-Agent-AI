from sqlalchemy import Column, String, Integer, Numeric, Boolean, Date, Time, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.db import Base

class Student(Base):
    __tablename__ = "students"
    
    student_id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    department = Column(String(50), nullable=False)
    semester = Column(Integer, nullable=False)
    attendance_pct = Column(Numeric(5, 2), default=0.0)

    registrations = relationship("CourseRegistration", back_populates="student")
    attendances = relationship("Attendance", back_populates="student")
    results = relationship("Result", back_populates="student")
    leave_requests = relationship("LeaveRequest", back_populates="student")


class Faculty(Base):
    __tablename__ = "faculty"
    
    faculty_id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    department = Column(String(50), nullable=False)
    designation = Column(String(50), nullable=False)
    office_room = Column(String(20))

    courses = relationship("Course", back_populates="instructor")
    approved_leaves = relationship("LeaveRequest", back_populates="reviewer")
    bookings = relationship("ClassroomBooking", back_populates="faculty")


class Course(Base):
    __tablename__ = "courses"
    
    course_code = Column(String(20), primary_key=True)
    course_name = Column(String(100), nullable=False)
    credits = Column(Integer, nullable=False)
    department = Column(String(50), nullable=False)
    faculty_id = Column(String(50), ForeignKey("faculty.faculty_id"))

    instructor = relationship("Faculty", back_populates="courses")
    registrations = relationship("CourseRegistration", back_populates="course")


class Prerequisite(Base):
    __tablename__ = "prerequisites"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    course_code = Column(String(20), ForeignKey("courses.course_code"))
    prereq_course_code = Column(String(20), ForeignKey("courses.course_code"))
    
    __table_args__ = (UniqueConstraint("course_code", "prereq_course_code", name="uix_course_prereq"),)


class CourseRegistration(Base):
    __tablename__ = "course_registrations"
    
    registration_id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(50), ForeignKey("students.student_id"))
    course_code = Column(String(20), ForeignKey("courses.course_code"))
    semester = Column(Integer, nullable=False)
    status = Column(String(20), default="enrolled")  # 'enrolled', 'completed', 'pending'
    grade = Column(String(2), default=None)

    student = relationship("Student", back_populates="registrations")
    course = relationship("Course", back_populates="registrations")
    
    __table_args__ = (UniqueConstraint("student_id", "course_code", name="uix_student_course"),)


class Attendance(Base):
    __tablename__ = "attendance"
    
    attendance_id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(50), ForeignKey("students.student_id"))
    course_code = Column(String(20), ForeignKey("courses.course_code"))
    date = Column(Date, nullable=False)
    status = Column(String(10), nullable=False)  # 'present', 'absent', 'late'

    student = relationship("Student", back_populates="attendances")
    
    __table_args__ = (UniqueConstraint("student_id", "course_code", "date", name="uix_student_course_date"),)


class Result(Base):
    __tablename__ = "results"
    
    result_id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(50), ForeignKey("students.student_id"))
    course_code = Column(String(20), ForeignKey("courses.course_code"))
    exam_type = Column(String(30), nullable=False)  # 'Midterm', 'Endsem', 'Quiz'
    marks_obtained = Column(Numeric(5, 2), nullable=False)
    max_marks = Column(Numeric(5, 2), nullable=False)

    student = relationship("Student", back_populates="results")
    
    __table_args__ = (UniqueConstraint("student_id", "course_code", "exam_type", name="uix_student_course_exam"),)


class LeaveRequest(Base):
    __tablename__ = "leave_requests"
    
    leave_id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(50), ForeignKey("students.student_id"))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    reason = Column(String, nullable=False)
    status = Column(String(20), default="pending")  # 'pending', 'approved', 'rejected'
    reviewed_by = Column(String(50), ForeignKey("faculty.faculty_id"))
    review_comments = Column(String)

    student = relationship("Student", back_populates="leave_requests")
    reviewer = relationship("Faculty", back_populates="approved_leaves")


class Classroom(Base):
    __tablename__ = "classrooms"
    
    room_number = Column(String(20), primary_key=True)
    building = Column(String(50), nullable=False)
    capacity = Column(Integer, nullable=False)
    has_projector = Column(Boolean, default=True)


class ClassroomBooking(Base):
    __tablename__ = "classroom_bookings"
    
    booking_id = Column(Integer, primary_key=True, autoincrement=True)
    room_number = Column(String(20), ForeignKey("classrooms.room_number"))
    booked_by = Column(String(50), ForeignKey("faculty.faculty_id"))
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    purpose = Column(String(100), nullable=False)

    faculty = relationship("Faculty", back_populates="bookings")
