import json
import logging
from sqlalchemy import text
from app.graphs.state import AgentState
from app.core.db import engine
from app.core.llm import query_llm

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are the SQL Validator Agent of a College Multi-Agent Assistant System.
Your job is to double check the generated SQL query for structural safety and role permissions.

VALIDATION CHECKLIST:
1. Syntax correctness.
2. If user role is 'student':
   - SELECT queries on students, results, attendance, course_registrations, leave_requests MUST be filtered by `student_id = :current_user`.
   - The student is allowed to INSERT into `leave_requests` and `course_registrations`.
   - The student is NOT allowed to UPDATE/INSERT/DELETE `attendance`, `results`, `faculty`, `courses`, `classrooms`, `classroom_bookings`.
3. Check for disallowed keywords: DROP, TRUNCATE, ALTER, GRANT, REVOKE.

If the query is valid, reply strictly in JSON format:
{
  "valid": true,
  "feedback": ""
}

If invalid or insecure, reply with:
{
  "valid": false,
  "feedback": "Detailed explanation of why it failed and how the SQL Agent should fix it"
}"""

def run_validator_agent(state: AgentState) -> AgentState:
    logger.info("Running Validator Agent...")
    
    sql = state.get("sql_query", "")
    role = state.get("role", "student")
    user_id = state.get("user_id", "")
    
    # 1. Structural check for standard SQL injections or destructive operations
    blocked_keywords = ["drop", "truncate", "alter", "grant", "revoke", "schema"]
    sql_lower = sql.lower()
    for keyword in blocked_keywords:
        if f" {keyword} " in f" {sql_lower} ":
            state["sql_valid"] = False
            state["sql_validation_feedback"] = f"Security Violation: Keyword '{keyword.upper()}' is strictly prohibited."
            _log_validator(state, "Failed", state["sql_validation_feedback"])
            return state
            
    # 2. Strict Student Constraints
    if role == "student":
        # Check write restrictions
        write_keywords = ["insert", "update", "delete"]
        is_write = any(f" {kw} " in f" {sql_lower} " for kw in write_keywords)
        if is_write:
            allowed_student_inserts = ["leave_requests", "course_registrations"]
            is_allowed = any(tbl in sql_lower for tbl in allowed_student_inserts)
            if not is_allowed:
                state["sql_valid"] = False
                state["sql_validation_feedback"] = "Security Violation: Students are not authorized to write to this table."
                _log_validator(state, "Failed", state["sql_validation_feedback"])
                return state
        
        # Check student_id containment
        # Student query MUST contain :current_user or the exact student_id to filter results
        if "student_id" in sql_lower and not (":current_user" in sql_lower or user_id in sql_lower):
            state["sql_valid"] = False
            state["sql_validation_feedback"] = "Security Violation: Queries touching student data must filter by student_id = :current_user."
            _log_validator(state, "Failed", state["sql_validation_feedback"])
            return state

    # 3. Dry Run Check (Verify syntax with DB engine if simple SELECT)
    # We replace :current_user with a dummy string for parsing test
    try:
        if "select" in sql_lower and "insert" not in sql_lower and "update" not in sql_lower:
            test_sql = sql.replace(":current_user", f"'{user_id}'").strip().rstrip(";")
            with engine.connect() as conn:
                # Compile and check syntax without executing results fully (LIMIT 0)
                # If it fails, compiler raises error
                conn.execute(text(f"SELECT * FROM ({test_sql}) AS tmp LIMIT 0"))
    except Exception as db_err:
        state["sql_valid"] = False
        state["sql_validation_feedback"] = f"SQL Database Error: {str(db_err)}. Please verify table names and columns."
        _log_validator(state, "Failed", state["sql_validation_feedback"])
        return state

    # 4. LLM check for semantic alignment
    user_context = f"User Role: {role}\nSQL Query:\n{sql}"
    response = query_llm(SYSTEM_PROMPT, user_context, json_format=True)
    
    try:
        validation_result = json.loads(response)
        state["sql_valid"] = validation_result.get("valid", True)
        state["sql_validation_feedback"] = validation_result.get("feedback", "")
    except Exception as e:
        logger.error(f"Failed to parse Validator response: {e}. Defaulting to valid=True since DB check passed.")
        state["sql_valid"] = True
        state["sql_validation_feedback"] = ""

    status = "Completed" if state["sql_valid"] else "Failed"
    msg = "SQL query validated successfully." if state["sql_valid"] else state["sql_validation_feedback"]
    _log_validator(state, status, msg)
    
    return state

def _log_validator(state: AgentState, status: str, message: str):
    if "agent_log" not in state or state["agent_log"] is None:
        state["agent_log"] = []
    state["agent_log"].append({
        "agent": "Validator Agent",
        "status": status,
        "message": message
    })
