import logging
from app.graphs.state import AgentState
from app.core.vector_db import retrieve_documents

logger = logging.getLogger(__name__)

def run_rag_tool(state: AgentState) -> AgentState:
    logger.info("Running RAG Tool...")
    
    query = state.get("user_query", "")
    
    try:
        retrieved = retrieve_documents(query, limit=3)
        state["retrieved_docs"] = retrieved
        msg = f"Retrieved {len(retrieved)} relevant policy sections."
    except Exception as e:
        logger.error(f"RAG Tool Error: {e}")
        state["retrieved_docs"] = []
        msg = f"Failed to retrieve context: {str(e)}"
        
    if "agent_log" not in state or state["agent_log"] is None:
        state["agent_log"] = []
        
    state["agent_log"].append({
        "agent": "RAG Tool",
        "status": "Completed",
        "message": msg
    })
    
    return state
