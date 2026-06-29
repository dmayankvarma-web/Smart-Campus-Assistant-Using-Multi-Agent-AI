import json
import requests
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

def query_llm(system_prompt: str, user_prompt: str, json_format: bool = False) -> str:
    """
    Sends a query to local Ollama instance. Falls back to smart mock generator
    if Ollama is offline or fails.
    """
    try:
        url = f"{settings.OLLAMA_HOST}/api/chat"
        payload = {
            "model": settings.OLLAMA_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "stream": False
        }
        if json_format:
            payload["format"] = "json"
            
        response = requests.post(url, json=payload, timeout=8)
        if response.status_code == 200:
            result_json = response.json()
            return result_json["message"]["content"]
        else:
            raise ConnectionError(f"HTTP Error {response.status_code}")
    except Exception as e:
        logger.warning(f"Ollama request failed: {e}. Executing mock fallback.")
        return generate_mock_response(system_prompt, user_prompt, json_format)

def _get_query_words(user_prompt: str) -> set:
    query_line = ""
    for line in user_prompt.split("\n"):
        if "query:" in line.lower():
            query_line = line.lower().replace("query:", "").strip()
            break
    if not query_line:
        query_line = user_prompt.lower()
    import re
    return set(re.findall(r'\b[a-z0-9_]+\b', query_line))

def generate_mock_response(system_prompt: str, user_prompt: str, json_format: bool) -> str:
    """
    Fallback deterministic mock generator for testing when Ollama is not running.
    """
    user_prompt_lower = user_prompt.lower()
    
    # 1. Guardrail Agent mock response
    if "guardrail agent" in system_prompt.lower():
        # Check if the query is related to the project/database context
        related_keywords = {
            "attendance", "pct", "present", "absent",
            "course", "courses", "subject", "credit", "enrolled", "completed", "grade", "mark", "result", "exam", "endsem",
            "leave", "request", "sick", "medical", "wedding", "reason", "pending", "approved", "rejected",
            "faculty", "professor", "teacher", "hod", "office", "room", "building", "classroom", "booking", "capacity", "projector",
            "student", "students", "profile", "id", "department", "semester", "email",
            "hi", "hello", "hey", "help", "who are you", "what are you", "assistant", "system", "thank"
        }
        
        query_words = _get_query_words(user_prompt)
        
        # If the query does not contain any of the related keywords, block it as out of context
        if not (query_words & related_keywords):
            query_line_clean = " ".join(query_words)
            if not any(g in query_line_clean for g in ["who are you", "what are you"]):
                return json.dumps({"allowed": False, "reason": "The question you asked is out of context"})

        # Block if student wants to modify attendance
        if any(w in user_prompt_lower for w in ["modify", "change", "update", "set"]) and "attendance" in user_prompt_lower:
            return json.dumps({"allowed": False, "reason": "Students are not permitted to modify attendance records."})
        # Block if student wants to view another student's data
        if "student_id" in user_prompt_lower and "192125023" in user_prompt_lower and "192125022" in user_prompt_lower:
            if "role: student" in user_prompt_lower:
                return json.dumps({"allowed": False, "reason": "Access blocked: Students cannot access other students' records."})
        # Block if student wants to view confidential faculty details
        if "faculty" in user_prompt_lower and any(w in user_prompt_lower for w in ["salary", "password", "confidential"]):
            return json.dumps({"allowed": False, "reason": "Access blocked: Faculty confidential information is restricted."})
        # Default allow
        return json.dumps({"allowed": True, "reason": ""})
        
    # 2. Supervisor router mock response
    elif "supervisor agent" in system_prompt.lower():
        query_words = _get_query_words(user_prompt)
        sql_keywords = {
            "attendance", "course", "courses", "grade", "result", "classroom", "booking", "leave", "register",
            "student", "students", "faculty", "teacher", "list", "class"
        }
        rag_keywords = {
            "policy", "handbook", "regulation", "rule", "bus", "route"
        }
        
        if query_words & sql_keywords:
            return json.dumps({"route": "sql", "reason": "Requires querying database records."})
        elif query_words & rag_keywords:
            return json.dumps({"route": "rag", "reason": "Requires reading unstructured policy documents."})
        else:
            return json.dumps({"route": "memory", "reason": "Conversation or greeting/followup query."})

    # 3. SQL Agent mock response
    elif "sql query agent" in system_prompt.lower():
        is_faculty = "role: faculty" in user_prompt_lower
        
        if is_faculty:
            # Faculty specific queries
            if "attendance" in user_prompt_lower:
                return "SELECT student_id, course_code, date, status FROM attendance JOIN courses ON attendance.course_code = courses.course_code WHERE courses.faculty_id = :current_user;"
            elif "course" in user_prompt_lower or "teach" in user_prompt_lower:
                return "SELECT course_code, course_name, credits, department FROM courses WHERE faculty_id = :current_user;"
            elif "student" in user_prompt_lower:
                return "SELECT student_id, name, email, department, semester, attendance_pct FROM students WHERE department = (SELECT department FROM faculty WHERE faculty_id = :current_user);"
            elif "classroom" in user_prompt_lower or "booking" in user_prompt_lower:
                return "SELECT room_number, date, start_time, end_time, purpose FROM classroom_bookings WHERE booked_by = :current_user;"
            elif "leave" in user_prompt_lower:
                return "SELECT leave_id, student_id, start_date, end_date, reason, status FROM leave_requests JOIN students ON leave_requests.student_id = students.student_id WHERE students.department = (SELECT department FROM faculty WHERE faculty_id = :current_user);"
            else:
                return "SELECT course_code, course_name, credits, department FROM courses WHERE faculty_id = :current_user;"
        else:
            # Student specific queries
            if "attendance" in user_prompt_lower:
                if "overall" in user_prompt_lower or "percentage" in user_prompt_lower:
                    return "SELECT name, attendance_pct FROM students WHERE student_id = :current_user;"
                return "SELECT date, course_code, status FROM attendance WHERE student_id = :current_user ORDER BY date DESC;"
            elif "course" in user_prompt_lower:
                if "enrolled" in user_prompt_lower:
                    return "SELECT c.course_code, c.course_name, c.credits FROM course_registrations cr JOIN courses c ON cr.course_code = c.course_code WHERE cr.student_id = :current_user AND cr.status = 'enrolled';"
                if "pending" in user_prompt_lower:
                    return "SELECT c.course_code, c.course_name, c.credits FROM course_registrations cr JOIN courses c ON cr.course_code = c.course_code WHERE cr.student_id = :current_user AND cr.status = 'pending';"
                if "prerequisite" in user_prompt_lower or "pre-req" in user_prompt_lower:
                    return "SELECT course_code, prereq_course_code FROM prerequisites;"
                return "SELECT c.course_code, c.course_name, c.credits, c.department FROM course_registrations cr JOIN courses c ON cr.course_code = c.course_code WHERE cr.student_id = :current_user;"
            elif "faculty" in user_prompt_lower:
                return "SELECT name, email, department, designation, office_room FROM faculty;"
            elif "classroom" in user_prompt_lower:
                if "booking" in user_prompt_lower or "book" in user_prompt_lower:
                    return "SELECT room_number, date, start_time, end_time, purpose FROM classroom_bookings;"
                return "SELECT room_number, building, capacity, has_projector FROM classrooms;"
            elif "leave" in user_prompt_lower:
                return "SELECT leave_id, start_date, end_date, reason, status FROM leave_requests WHERE student_id = :current_user;"
            elif "result" in user_prompt_lower or "grade" in user_prompt_lower or "marks" in user_prompt_lower:
                return "SELECT course_code, exam_type, marks_obtained, max_marks FROM results WHERE student_id = :current_user;"
            else:
                return "SELECT * FROM students WHERE student_id = :current_user;"

    # 4. Validator Agent mock response
    elif "validator agent" in system_prompt.lower():
        return json.dumps({"valid": True, "feedback": ""})

    # 5. Response Generator mock response
    elif "response generator agent" in system_prompt.lower():
        if "sql database result" in user_prompt_lower:
            try:
                import ast
                marker = "SQL Database Result: "
                idx = user_prompt.find(marker)
                if idx != -1:
                    result_str = user_prompt[idx + len(marker):].strip()
                    result_str = result_str.split("\n")[0]
                    records = ast.literal_eval(result_str)
                    
                    if isinstance(records, list):
                        if len(records) == 0:
                            return "No matching records were found in your database profile."
                        
                        first_rec = records[0]
                        
                        # 1. Overall Attendance Percentage Query
                        if "attendance_pct" in first_rec and "name" in first_rec and len(first_rec) <= 3:
                            name = first_rec.get("name", "Student")
                            pct = first_rec.get("attendance_pct", 0)
                            return f"Your overall attendance percentage is **{pct}%**."
                            
                        # 2. Student List Query (for Faculty)
                        elif "student_id" in first_rec and "attendance_pct" in first_rec:
                            res = "Here is the list of students in your department:\n\n"
                            for r in records:
                                res += f"• **{r.get('name')}** (ID: {r.get('student_id')}) - Semester {r.get('semester')} ({r.get('department')})\n"
                                res += f"  - Email: {r.get('email')}\n"
                                res += f"  - Attendance: **{r.get('attendance_pct')}%**\n\n"
                            return res.strip()
                            
                        # 3. Detailed Attendance Logs Query
                        elif "status" in first_rec and "date" in first_rec:
                            res = "Based on your records, here is the student attendance log:\n\n"
                            for r in records:
                                student_str = f"Student {r.get('student_id')}: " if "student_id" in r else ""
                                res += f"• {student_str}**{r.get('date')}** - {r.get('course_code')} (*{r.get('status').capitalize()}*)\n"
                            return res.strip()
                            
                        # 4. Course Enrolled/List Query
                        elif "course_name" in first_rec:
                            res = "Here are the courses found in your profile:\n\n"
                            for r in records:
                                credits_str = f" ({r.get('credits')} credits)" if "credits" in r else ""
                                dept_str = f" - *{r.get('department')}*" if "department" in r else ""
                                res += f"• **{r.get('course_name')}** ({r.get('course_code')}){credits_str}{dept_str}\n"
                            return res.strip()
                            
                        # 5. Classroom Bookings
                        elif "room_number" in first_rec and "purpose" in first_rec:
                            res = "Here are the classroom bookings:\n\n"
                            for r in records:
                                date_str = f" on **{r.get('date')}**" if "date" in r else ""
                                time_str = f" from **{r.get('start_time')}** to **{r.get('end_time')}**" if "start_time" in r else ""
                                res += f"• **Room {r.get('room_number')}** for *\"{r.get('purpose')}\"*{date_str}{time_str}\n"
                            return res.strip()
                            
                        # 6. Leave Requests Query
                        elif "reason" in first_rec and "status" in first_rec:
                            res = "Here are the leave request details:\n\n"
                            for r in records:
                                student_str = f"Student: **{r.get('student_name', r.get('student_id'))}**\n" if ("student_name" in r or "student_id" in r) else ""
                                res += f"• {student_str}Duration: **{r.get('start_date')}** to **{r.get('end_date')}**\n"
                                res += f"  - Reason: {r.get('reason')}\n"
                                res += f"  - Status: *{r.get('status').capitalize()}*\n"
                                if r.get("review_comments"):
                                    res += f"  - HOD Comments: \"{r.get('review_comments')}\"\n"
                                res += "\n"
                            return res.strip()
                            
                        # 7. Results / Grades Query
                        elif "marks_obtained" in first_rec or "grade" in first_rec:
                            res = "Here are your academic results:\n\n"
                            for r in records:
                                if "grade" in r:
                                    res += f"• **{r.get('course_code')}**: Grade *{r.get('grade')}* (Status: {r.get('status')})\n"
                                else:
                                    res += f"• **{r.get('course_code')}** ({r.get('exam_type')}): **{r.get('marks_obtained')}** / {r.get('max_marks')} marks\n"
                            return res.strip()
                            
                        # Generic fallback formatter for lists of dicts
                        formatted_response = "Here are the records matching your profile:\n\n"
                        for i, rec in enumerate(records, 1):
                            details = ", ".join(f"**{k.replace('_', ' ').title()}**: {v}" for k, v in rec.items())
                            formatted_response += f"{i}. {details}\n"
                        return formatted_response.strip()
            except Exception as e:
                logger.error(f"Error compiling dynamic mock response: {e}")
            return "Here are the database records matching your query:\n" + user_prompt
            
        if "retrieved_docs" in user_prompt_lower:
            if "leave" in user_prompt_lower or "attendance" in user_prompt_lower:
                return "According to the student policies, you must maintain a minimum of **75% overall attendance** to be eligible for final semester examinations. Medical leaves must be submitted within 7 working days with a valid certificate. [Source: Student Handbook Sec 4.2]"
            return "According to the college rules:\n" + user_prompt
            
        return "Hello! I am your college assistant. How can I help you check courses, attendance, leaves, or regulations today?"

        
    return "This is a placeholder assistant response."
