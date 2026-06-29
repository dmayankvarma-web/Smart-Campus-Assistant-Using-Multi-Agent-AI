import os
import json
import logging
from datetime import datetime
from app.graphs.state import AgentState

logger = logging.getLogger(__name__)

MEMORY_DIR = "./conversations_memory"
os.makedirs(MEMORY_DIR, exist_ok=True)

def load_user_memory(user_id: str, username: str, role: str) -> dict:
    filepath = os.path.join(MEMORY_DIR, f"{user_id}.json")
    if os.path.exists(filepath):
        try:
            with open(filepath, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading memory for user {user_id}: {e}")
            
    # Default memory structure
    return {
        "user_id": user_id,
        "username": username,
        "role": role,
        "sessions": []
    }

def save_user_memory(user_id: str, memory_data: dict):
    filepath = os.path.join(MEMORY_DIR, f"{user_id}.json")
    try:
        with open(filepath, "w") as f:
            json.dump(memory_data, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving memory for user {user_id}: {e}")

def add_message_to_session(user_id: str, username: str, role: str, session_id: str, user_msg: str, assistant_msg: str):
    memory = load_user_memory(user_id, username, role)
    
    # Find or create session
    session = None
    for s in memory["sessions"]:
        if s["session_id"] == session_id:
            session = s
            break
            
    if not session:
        session = {
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat(),
            "messages": []
        }
        memory["sessions"].append(session)
        
    session["messages"].append({"role": "user", "content": user_msg})
    session["messages"].append({"role": "assistant", "content": assistant_msg})
    
    save_user_memory(user_id, memory)

def run_memory_tool(state: AgentState) -> AgentState:
    logger.info("Running Memory Tool...")
    # This node prepares conversational context for response generation
    # if the supervisor routes to memory
    user_id = state.get("user_id", "")
    username = state.get("username", "")
    role = state.get("role", "")
    
    memory = load_user_memory(user_id, username, role)
    
    # Extract recent conversation summary or list of messages for context
    # We will log it in agent activity
    recent_count = 0
    if memory["sessions"]:
        recent_count = len(memory["sessions"][-1]["messages"])
        
    if "agent_log" not in state or state["agent_log"] is None:
        state["agent_log"] = []
        
    state["agent_log"].append({
        "agent": "Memory Tool",
        "status": "Completed",
        "message": f"Loaded context. Previous interaction turns found: {recent_count // 2}."
    })
    
    return state
