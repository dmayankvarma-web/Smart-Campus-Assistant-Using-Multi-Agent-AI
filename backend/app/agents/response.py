import logging
from app.graphs.state import AgentState
from app.core.llm import query_llm

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are the Response Generator Agent of a College Multi-Agent Assistant System.
Your job is to synthesize all gathered information and generate a natural, friendly, and accurate response to the user.

INSTRUCTIONS:
1. Provide a direct and comprehensive answer.
2. Format lists and tables nicely using Markdown where appropriate.
3. If RAG documents are used, cite the source documents (e.g. "[Source: Student Handbook Sec 4.2]").
4. Never expose raw SQL queries or DB column names directly to the user.
5. If the request was blocked by the guardrail, explain politely.
"""

def run_response_agent(state: AgentState) -> AgentState:
    logger.info("Running Response Generator Agent...")
    
    # Check if blocked
    if not state.get("guardrail_allowed", True):
        reason = state.get("guardrail_reason", "Access denied.")
        if reason == "The question you asked is out of context":
            state["response_content"] = reason
        else:
            state["response_content"] = f"Request Blocked: {reason}"
        _log_response(state)
        return state
        
    route = state.get("route", "memory")
    user_query = state.get("user_query", "")
    
    context = f"User Query: {user_query}\n"
    context += f"Route Selected: {route}\n"
    
    if route == "sql":
        context += f"Executed SQL: {state.get('sql_query', '')}\n"
        context += f"SQL Database Result: {state.get('sql_result', [])}\n"
    elif route == "rag":
        context += f"Retrieved Documents:\n"
        for doc in state.get("retrieved_docs", []):
            context += f"- Content: {doc['content']}\n  Source: {doc['source']}\n"
    else:
        context += "No additional tools needed. Respond conversationally using history if needed.\n"

    response = query_llm(SYSTEM_PROMPT, context)
    state["response_content"] = response
    
    _log_response(state)
    return state

def _log_response(state: AgentState):
    if "agent_log" not in state or state["agent_log"] is None:
        state["agent_log"] = []
    state["agent_log"].append({
        "agent": "Response Generator",
        "status": "Completed",
        "message": "Final answer synthesized and formatted."
    })
