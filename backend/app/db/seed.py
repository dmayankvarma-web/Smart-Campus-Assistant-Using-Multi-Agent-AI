from sqlalchemy.orm import Session
from datetime import date, time, timedelta
from app.core.db import engine, Base, SessionLocal
from app.core.security import get_password_hash
from app.db.models import Student, Faculty, Course, Prerequisite, CourseRegistration, Attendance, Result, LeaveRequest, Classroom, ClassroomBooking

def seed_db(db: Session):
    # Check if we have the new courses seeded
    has_new_courses = db.query(Course).filter(Course.course_code == "ME301").first() is not None
    bhavani_exists = db.query(Student).filter(Student.name == "Bhavani").first() is not None
    if db.query(Student).count() >= 15 and not bhavani_exists and has_new_courses:
        print("Database already seeded with sufficient students and new courses.")
        return
        
    print("Outdated database found. Dropping and re-seeding all tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    hashed_pw = get_password_hash("password123")

    # 1. Seed Faculty
    f1 = Faculty(faculty_id="F101", name="Dr. Amit Sharma", email="amit.sharma@college.edu", hashed_password=hashed_pw, department="Computer Science", designation="Professor", office_room="B-302")
    f2 = Faculty(faculty_id="F102", name="Prof. Priya Patel", email="priya.patel@college.edu", hashed_password=hashed_pw, department="Electrical Engineering", designation="Assistant Professor", office_room="E-104")
    f3 = Faculty(faculty_id="F103", name="Dr. Rajesh Kumar", email="rajesh.kumar@college.edu", hashed_password=hashed_pw, department="Mathematics", designation="Associate Professor", office_room="M-201")
    f4 = Faculty(faculty_id="F104", name="Dr. Vikram Malhotra", email="vikram.malhotra@college.edu", hashed_password=hashed_pw, department="Computer Science", designation="Professor", office_room="B-305")
    f5 = Faculty(faculty_id="F105", name="Prof. Sangeeta Rao", email="sangeeta.rao@college.edu", hashed_password=hashed_pw, department="Electronics & Communication", designation="Assistant Professor", office_room="C-204")
    f6 = Faculty(faculty_id="F106", name="Dr. Anil Deshmukh", email="anil.deshmukh@college.edu", hashed_password=hashed_pw, department="Mechanical Engineering", designation="Associate Professor", office_room="M-102")
    f7 = Faculty(faculty_id="F107", name="Prof. Kavita Sen", email="kavita.sen@college.edu", hashed_password=hashed_pw, department="Computer Science", designation="Assistant Professor", office_room="B-108")
    f8 = Faculty(faculty_id="F108", name="Dr. Ramesh Nair", email="ramesh.nair@college.edu", hashed_password=hashed_pw, department="Mechanical Engineering", designation="Professor", office_room="M-205")
    db.add_all([f1, f2, f3, f4, f5, f6, f7, f8])
    db.commit()

    # 2. Seed 15 Students
    students_data = [
        ("192125022", "Aditya", "aditya@college.edu", "Computer Science", 6, 88.00),
        ("192125023", "Arjun", "arjun@college.edu", "Computer Science", 6, 76.50),
        ("192125024", "Neha Sen", "neha@college.edu", "Electrical Engineering", 4, 92.10),
        ("192125025", "Rahul Sharma", "rahul.sharma@college.edu", "Computer Science", 6, 84.00),
        ("192125026", "Priyanka Rao", "priyanka.rao@college.edu", "Electrical Engineering", 4, 78.20),
        ("192125027", "Amit Patel", "amit.patel@college.edu", "Mechanical Engineering", 2, 65.00),
        ("192125028", "Sneha Reddy", "sneha.reddy@college.edu", "Electronics & Communication", 6, 89.40),
        ("192125029", "Vikram Singh", "vikram.singh@college.edu", "Computer Science", 4, 72.80),
        ("192125030", "Pooja Nair", "pooja.nair@college.edu", "Electrical Engineering", 6, 81.50),
        ("192125031", "Rohan Das", "rohan.das@college.edu", "Mechanical Engineering", 4, 69.20),
        ("192125032", "Ananya Joshi", "ananya.joshi@college.edu", "Computer Science", 2, 95.00),
        ("192125033", "Siddharth Roy", "siddharth.roy@college.edu", "Electronics & Communication", 4, 87.30),
        ("192125034", "Divya Murthy", "divya.murthy@college.edu", "Electrical Engineering", 2, 74.00),
        ("192125035", "Karan Malhotra", "karan.malhotra@college.edu", "Computer Science", 6, 91.20),
        ("192125036", "Meera Krishnan", "meera.krishnan@college.edu", "Electronics & Communication", 2, 83.10),
    ]
    
    students = []
    for sid, name, email, dept, sem, att in students_data:
        student = Student(student_id=sid, name=name, email=email, hashed_password=hashed_pw, department=dept, semester=sem, attendance_pct=att)
        students.append(student)
        db.add(student)
    db.commit()

    # 3. Seed Courses
    c1 = Course(course_code="CS101", course_name="Introduction to Programming", credits=4, department="Computer Science", faculty_id="F101")
    c2 = Course(course_code="CS102", course_name="Data Structures & Algorithms", credits=4, department="Computer Science", faculty_id="F104")
    c3 = Course(course_code="CS301", course_name="Database Management Systems", credits=3, department="Computer Science", faculty_id="F107")
    c4 = Course(course_code="CS302", course_name="Operating Systems", credits=4, department="Computer Science", faculty_id="F104")
    c5 = Course(course_code="EE201", course_name="Network Analysis", credits=3, department="Electrical Engineering", faculty_id="F102")
    c6 = Course(course_code="EE202", course_name="Control Systems", credits=3, department="Electrical Engineering", faculty_id="F102")
    c7 = Course(course_code="EC101", course_name="Basic Electronics", credits=3, department="Electronics & Communication", faculty_id="F105")
    c8 = Course(course_code="EC301", course_name="Digital Signal Processing", credits=4, department="Electronics & Communication", faculty_id="F105")
    c9 = Course(course_code="ME101", course_name="Engineering Mechanics", credits=3, department="Mechanical Engineering", faculty_id="F106")
    c10 = Course(course_code="ME301", course_name="Thermodynamics", credits=4, department="Mechanical Engineering", faculty_id="F108")
    c11 = Course(course_code="MA101", course_name="Calculus & Linear Algebra", credits=4, department="Mathematics", faculty_id="F103")
    c12 = Course(course_code="MA201", course_name="Probability & Statistics", credits=4, department="Mathematics", faculty_id="F103")
    db.add_all([c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12])
    db.commit()

    # 4. Seed Prerequisites
    p1 = Prerequisite(course_code="CS102", prereq_course_code="CS101")
    p2 = Prerequisite(course_code="CS301", prereq_course_code="CS102")
    db.add_all([p1, p2])
    db.commit()

    # 5. Seed Course Registrations & Attendance & Results
    today = date.today()
    for s in students:
        if s.department == "Computer Science":
            # CS Students
            if s.semester == 2:
                # Sem 2 CS Students: enrolled in CS101, MA101
                db.add(CourseRegistration(student_id=s.student_id, course_code="CS101", semester=2, status="enrolled"))
                db.add(CourseRegistration(student_id=s.student_id, course_code="MA101", semester=2, status="enrolled"))
                db.add(Attendance(student_id=s.student_id, course_code="CS101", date=today, status="present"))
                db.add(Attendance(student_id=s.student_id, course_code="MA101", date=today, status="present"))
            elif s.semester == 4:
                # Sem 4 CS Students: completed CS101, enrolled in CS102, MA201
                db.add(CourseRegistration(student_id=s.student_id, course_code="CS101", semester=2, status="completed", grade="A-"))
                db.add(CourseRegistration(student_id=s.student_id, course_code="CS102", semester=4, status="enrolled"))
                db.add(CourseRegistration(student_id=s.student_id, course_code="MA201", semester=4, status="enrolled"))
                db.add(Attendance(student_id=s.student_id, course_code="CS102", date=today, status="present"))
                db.add(Result(student_id=s.student_id, course_code="CS101", exam_type="Endsem", marks_obtained=87.0, max_marks=100.0))
            else:
                # Sem 6 CS Students: completed CS101, CS102, enrolled in CS301, CS302
                db.add(CourseRegistration(student_id=s.student_id, course_code="CS101", semester=2, status="completed", grade="A"))
                db.add(CourseRegistration(student_id=s.student_id, course_code="CS102", semester=4, status="completed", grade="B+"))
                db.add(CourseRegistration(student_id=s.student_id, course_code="CS301", semester=6, status="enrolled"))
                db.add(CourseRegistration(student_id=s.student_id, course_code="CS302", semester=6, status="enrolled"))
                db.add(Attendance(student_id=s.student_id, course_code="CS301", date=today - timedelta(days=1), status="present"))
                db.add(Attendance(student_id=s.student_id, course_code="CS301", date=today, status="present" if s.attendance_pct > 80 else "absent"))
                db.add(Result(student_id=s.student_id, course_code="CS101", exam_type="Endsem", marks_obtained=90.0, max_marks=100.0))
                db.add(Result(student_id=s.student_id, course_code="CS102", exam_type="Endsem", marks_obtained=84.5, max_marks=100.0))
            
        elif s.department == "Electrical Engineering":
            # EE Students
            if s.semester == 2:
                db.add(CourseRegistration(student_id=s.student_id, course_code="EE201", semester=2, status="enrolled"))
                db.add(CourseRegistration(student_id=s.student_id, course_code="MA101", semester=2, status="enrolled"))
                db.add(Attendance(student_id=s.student_id, course_code="EE201", date=today, status="present"))
            elif s.semester == 4:
                db.add(CourseRegistration(student_id=s.student_id, course_code="CS101", semester=2, status="completed", grade="B"))
                db.add(CourseRegistration(student_id=s.student_id, course_code="EE202", semester=4, status="enrolled"))
                db.add(Attendance(student_id=s.student_id, course_code="EE202", date=today, status="present"))
            else:
                db.add(CourseRegistration(student_id=s.student_id, course_code="EE201", semester=4, status="completed", grade="A"))
                db.add(CourseRegistration(student_id=s.student_id, course_code="EE202", semester=6, status="enrolled"))
                db.add(CourseRegistration(student_id=s.student_id, course_code="MA201", semester=6, status="enrolled"))
                db.add(Attendance(student_id=s.student_id, course_code="EE202", date=today, status="present" if s.attendance_pct > 80 else "absent"))
                
        elif s.department == "Electronics & Communication":
            # EC Students
            if s.semester == 2:
                db.add(CourseRegistration(student_id=s.student_id, course_code="EC101", semester=2, status="enrolled"))
                db.add(CourseRegistration(student_id=s.student_id, course_code="MA101", semester=2, status="enrolled"))
                db.add(Attendance(student_id=s.student_id, course_code="EC101", date=today, status="present"))
            elif s.semester == 4:
                db.add(CourseRegistration(student_id=s.student_id, course_code="MA101", semester=2, status="completed", grade="B-"))
                db.add(CourseRegistration(student_id=s.student_id, course_code="EC301", semester=4, status="enrolled"))
                db.add(Attendance(student_id=s.student_id, course_code="EC301", date=today, status="present"))
            else:
                db.add(CourseRegistration(student_id=s.student_id, course_code="EC101", semester=2, status="completed", grade="A-"))
                db.add(CourseRegistration(student_id=s.student_id, course_code="EC301", semester=6, status="enrolled"))
                db.add(CourseRegistration(student_id=s.student_id, course_code="EE201", semester=6, status="enrolled"))
                db.add(Attendance(student_id=s.student_id, course_code="EC301", date=today, status="present"))

        elif s.department == "Mechanical Engineering":
            # ME Students
            if s.semester == 2:
                db.add(CourseRegistration(student_id=s.student_id, course_code="ME101", semester=2, status="enrolled"))
                db.add(CourseRegistration(student_id=s.student_id, course_code="MA101", semester=2, status="enrolled"))
                db.add(Attendance(student_id=s.student_id, course_code="ME101", date=today, status="present"))
            elif s.semester == 4:
                db.add(CourseRegistration(student_id=s.student_id, course_code="MA101", semester=2, status="completed", grade="C+"))
                db.add(CourseRegistration(student_id=s.student_id, course_code="ME301", semester=4, status="enrolled"))
                db.add(Attendance(student_id=s.student_id, course_code="ME301", date=today, status="present"))
            else:
                db.add(CourseRegistration(student_id=s.student_id, course_code="ME101", semester=2, status="completed", grade="B+"))
                db.add(CourseRegistration(student_id=s.student_id, course_code="ME301", semester=6, status="enrolled"))
                db.add(CourseRegistration(student_id=s.student_id, course_code="MA201", semester=6, status="enrolled"))
                db.add(Attendance(student_id=s.student_id, course_code="ME301", date=today, status="present"))

    db.commit()

    # 6. Seed Leave Requests
    db.add(LeaveRequest(student_id="192125022", start_date=today + timedelta(days=5), end_date=today + timedelta(days=7), reason="Family wedding", status="pending"))
    db.add(LeaveRequest(student_id="192125023", start_date=today - timedelta(days=10), end_date=today - timedelta(days=9), reason="Medical checkup", status="approved", reviewed_by="F101", review_comments="Approved. Take care."))
    db.add(LeaveRequest(student_id="192125025", start_date=today + timedelta(days=2), end_date=today + timedelta(days=3), reason="Hackathon participation", status="pending"))
    db.add(LeaveRequest(student_id="192125028", start_date=today - timedelta(days=4), end_date=today - timedelta(days=2), reason="Sick leave", status="approved", reviewed_by="F101", review_comments="Get well soon."))
    db.commit()

    # 7. Seed Classrooms
    cr1 = Classroom(room_number="R101", building="CS Block", capacity=60, has_projector=True)
    cr2 = Classroom(room_number="R102", building="CS Block", capacity=40, has_projector=False)
    cr3 = Classroom(room_number="E201", building="Electrical Block", capacity=80, has_projector=True)
    db.add_all([cr1, cr2, cr3])
    db.commit()

    # 8. Seed Classroom Bookings
    b_date = today + timedelta(days=1)
    cb1 = ClassroomBooking(room_number="R101", booked_by="F101", date=b_date, start_time=time(9, 0), end_time=time(11, 0), purpose="Extra DSA Class")
    cb2 = ClassroomBooking(room_number="E201", booked_by="F102", date=b_date, start_time=time(14, 0), end_time=time(16, 0), purpose="Lab review")
    db.add_all([cb1, cb2])
    db.commit()

    print("Database seeding completed.")

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_db(db)
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
