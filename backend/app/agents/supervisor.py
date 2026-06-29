import json
import logging
from app.graphs.state import AgentState
from app.core.llm import query_llm

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are the Supervisor Agent of a College Multi-Agent Assistant System.
Your task is to analyze the user query and decide the appropriate processing path (route).

Path Choices:
- 'sql': Use this path if the query requires structured institutional data, such as:
  * Checking attendance records
  * Retrieving course lists, prerequisites, or registrations
  * Looking up grades, results, exam scores
  * Checking classroom capacity, availability, or bookings
  * Managing leave requests (submitting, viewing, approving, rejecting)
  * Retrieving specific details about students or faculty from database tables
- 'rag': Use this path if the query asks about unstructured documents, policies, or general knowledge:
  * College Handbook rules, discipline codes
  * Leave Policies & attendance requirement percentages rules (e.g. minimum 75%)
  * Academic Regulations (how registration works in general, grading system weighting)
  * Examination rules (midterm/endsem ratios)
  * Infrastructure buildings general descriptions
  * Bus routes, pickup times, main stops
- 'memory': Use this path if the query is a simple greeting (e.g. "hello", "hi"), a thank you, or a general follow-up question that doesn't need external data.

Reply strictly in JSON format:
{
  "route": "sql" or "rag" or "memory",
  "reason": "Brief explanation of your routing decision"
}"""

def run_supervisor_agent(state: AgentState) -> AgentState:
    logger.info("Running Supervisor Agent...")
    
    # Check if Guardrail already blocked the request
    if not state.get("guardrail_allowed", True):
        state["route"] = "blocked"
        if "agent_log" not in state or state["agent_log"] is None:
            state["agent_log"] = []
        state["agent_log"].append({
            "agent": "Supervisor Agent",
            "status": "Skipped",
            "message": "Query blocked by Guardrails."
        })
        return state

    user_context = f"Query: {state['user_query']}\nUser Role: {state['role']}"
    response = query_llm(SYSTEM_PROMPT, user_context, json_format=True)
    
    try:
        decision = json.loads(response)
        state["route"] = decision.get("route", "memory")
    except Exception as e:
        logger.error(f"Failed to parse Supervisor route: {e}. Defaulting to memory.")
        state["route"] = "memory"
        
    if "agent_log" not in state or state["agent_log"] is None:
        state["agent_log"] = []
        
    state["agent_log"].append({
        "agent": "Supervisor Agent",
        "status": "Completed",
        "message": f"Routed query to '{state['route'].upper()}' pipeline."
    })
    
    return state
