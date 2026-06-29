from typing import TypedDict, List, Dict, Any, Optional

class AgentStepLog(TypedDict):
    agent: str
    status: str
    message: str

class AgentState(TypedDict):
    # User session info
    user_id: str
    role: str
    username: str
    
    # Query details
    user_query: str
    
    # Guardrail decisions
    guardrail_allowed: bool
    guardrail_reason: str
    
    # Orchestrator routing
    route: str  # 'sql', 'rag', 'memory', 'blocked'
    
    # SQL generation loop variables
    sql_query: str
    sql_validation_feedback: str
    sql_validation_attempts: int
    sql_valid: bool
    sql_result: Optional[List[Dict[str, Any]]]
    
    # RAG outputs
    retrieved_docs: List[Dict[str, Any]]
    
    # Final generated answer
    response_content: str
    
    # Execution tracing logs for front-end visual update
    agent_log: List[AgentStepLog]
