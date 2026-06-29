import logging
from app.graphs.state import AgentState
from app.core.llm import query_llm

logger = logging.getLogger(__name__)

DB_SCHEMA_PROMPT = """You are the SQL Query Agent of a College Multi-Agent Assistant System.
Your task is to convert the user's natural language request into a single PostgreSQL-compatible SQL query.

DATABASE SCHEMA:
- students (student_id VARCHAR PRIMARY KEY, name VARCHAR, email VARCHAR, hashed_password VARCHAR, department VARCHAR, semester INT, attendance_pct NUMERIC)
- faculty (faculty_id VARCHAR PRIMARY KEY, name VARCHAR, email VARCHAR, hashed_password VARCHAR, department VARCHAR, designation VARCHAR, office_room VARCHAR)
- courses (course_code VARCHAR PRIMARY KEY, course_name VARCHAR, credits INT, department VARCHAR, faculty_id VARCHAR REFERENCES faculty)
- prerequisites (id INT PRIMARY KEY, course_code VARCHAR REFERENCES courses, prereq_course_code VARCHAR REFERENCES courses)
- course_registrations (registration_id INT PRIMARY KEY, student_id VARCHAR REFERENCES students, course_code VARCHAR REFERENCES courses, semester INT, status VARCHAR, grade VARCHAR)
- attendance (attendance_id INT PRIMARY KEY, student_id VARCHAR REFERENCES students, course_code VARCHAR REFERENCES courses, date DATE, status VARCHAR)
- results (result_id INT PRIMARY KEY, student_id VARCHAR REFERENCES students, course_code VARCHAR REFERENCES courses, exam_type VARCHAR, marks_obtained NUMERIC, max_marks NUMERIC)
- leave_requests (leave_id INT PRIMARY KEY, student_id VARCHAR REFERENCES students, start_date DATE, end_date DATE, reason TEXT, status VARCHAR, reviewed_by VARCHAR REFERENCES faculty, review_comments TEXT)
- classrooms (room_number VARCHAR PRIMARY KEY, building VARCHAR, capacity INT, has_projector BOOLEAN)
- classroom_bookings (booking_id INT PRIMARY KEY, room_number VARCHAR REFERENCES classrooms, booked_by VARCHAR REFERENCES faculty, date DATE, start_time TIME, end_time TIME, purpose VARCHAR)

SECURITY CONTRIANTS:
1. If the user's role is 'student', you MUST restrict database access to their own data using the student_id check. Use the placeholder ':current_user' for the current logged-in user's student_id (e.g. `WHERE student_id = :current_user`).
2. Never select passwords or hashed passwords.
3. Only output the raw SQL query. Do not wrap it in markdown code blocks or add explanations.

FEEDBACK FROM PREVIOUS ATTEMPT (if any):
{feedback}
"""

def run_sql_agent(state: AgentState) -> AgentState:
    logger.info("Running SQL Query Agent...")
    
    feedback = state.get("sql_validation_feedback", "")
    system_prompt = DB_SCHEMA_PROMPT.format(feedback=feedback if feedback else "None")
    
    user_context = f"""
    User Query: {state['user_query']}
    User ID: {state['user_id']}
    User Role: {state['role']}
    Previous Attempt Query: {state.get('sql_query', 'None')}
    """
    
    sql_response = query_llm(system_prompt, user_context).strip()
    
    # Clean SQL response of markdown code formatting if present
    if sql_response.startswith("```"):
        sql_lines = sql_response.splitlines()
        # Remove first and last line if they contain formatting
        if sql_lines[0].startswith("```"):
            sql_lines = sql_lines[1:]
        if sql_lines[-1].strip() == "```":
            sql_lines = sql_lines[:-1]
        sql_response = "\n".join(sql_lines).strip()
        
    state["sql_query"] = sql_response
    state["sql_validation_attempts"] = state.get("sql_validation_attempts", 0) + 1
    
    if "agent_log" not in state or state["agent_log"] is None:
        state["agent_log"] = []
        
    state["agent_log"].append({
        "agent": "SQL Query Agent",
        "status": "In Progress",
        "message": f"Generated SQL Query (Attempt {state['sql_validation_attempts']}): [Hidden]"
    })
    
    return state
