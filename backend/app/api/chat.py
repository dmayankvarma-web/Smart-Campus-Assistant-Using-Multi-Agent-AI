import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.api.auth import get_current_user
from app.graphs.workflow import app_workflow
from app.tools.memory_tool import add_message_to_session, load_user_memory

router = APIRouter(prefix="/chat", tags=["chat"])
logger = logging.getLogger(__name__)

class MessageRequest(BaseModel):
    message: str
    session_id: str

@router.post("/message")
def chat_message(payload: MessageRequest, user: dict = Depends(get_current_user)):
    user_id = user["sub"]
    role = user["role"]
    username = user["name"]
    
    # 1. Initialize state for LangGraph
    initial_state = {
        "user_id": user_id,
        "role": role,
        "username": username,
        "user_query": payload.message,
        "guardrail_allowed": True,
        "guardrail_reason": "",
        "route": "",
        "sql_query": "",
        "sql_validation_feedback": "",
        "sql_validation_attempts": 0,
        "sql_valid": False,
        "sql_result": None,
        "retrieved_docs": [],
        "response_content": "",
        "agent_log": []
    }
    
    # 2. Invoke LangGraph Workflow
    try:
        final_state = app_workflow.invoke(initial_state)
    except Exception as e:
        logger.error(f"Error in LangGraph flow execution: {e}")
        raise HTTPException(status_code=500, detail=f"Agent workflow execution failed: {str(e)}")
        
    # 3. Store conversation in JSON memory
    user_msg = payload.message
    assistant_msg = final_state.get("response_content", "Sorry, I encountered an internal processing issue.")
    add_message_to_session(
        user_id=user_id,
        username=username,
        role=role,
        session_id=payload.session_id,
        user_msg=user_msg,
        assistant_msg=assistant_msg
    )
    
    # Optional Langfuse Tracking
    # (Since Langfuse is requested, we can log details if credentials exist)
    # We will log the execution info for Langfuse if needed
    
    # 4. Return results with logs for the UI Agent Activity Panel
    return {
        "response": assistant_msg,
        "route": final_state.get("route", ""),
        "sql_query": final_state.get("sql_query", "") if final_state.get("route") == "sql" else None,
        "retrieved_docs": final_state.get("retrieved_docs", []) if final_state.get("route") == "rag" else [],
        "agent_log": final_state.get("agent_log", [])
    }

@router.get("/history")
def get_chat_history(user: dict = Depends(get_current_user)):
    user_id = user["sub"]
    username = user["name"]
    role = user["role"]
    
    memory = load_user_memory(user_id, username, role)
    return memory.get("sessions", [])
