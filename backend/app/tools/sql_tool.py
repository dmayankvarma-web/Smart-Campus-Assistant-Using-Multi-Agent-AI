import logging
from sqlalchemy import text
from app.graphs.state import AgentState
from app.core.db import engine

logger = logging.getLogger(__name__)

def execute_sql_tool(state: AgentState) -> AgentState:
    logger.info("Executing SQL Tool...")
    
    if not state.get("sql_valid", False):
        state["sql_result"] = [{"error": "SQL Query was not validated."}]
        _log_tool(state, "Failed", "Aborted execution due to failed validation.")
        return state

    sql = state.get("sql_query", "")
    user_id = state.get("user_id", "")
    
    try:
        # Bind :current_user placeholder to active session user_id
        statement = text(sql)
        
        with engine.connect() as conn:
            # Check if it is a write query (INSERT / UPDATE)
            sql_lower = sql.lower()
            is_write = any(kw in sql_lower for kw in ["insert", "update", "delete"])
            
            result = conn.execute(statement, {"current_user": user_id})
            
            if is_write:
                # Commit transactional writes (SQLite needs explicit commit for raw connection edits sometimes)
                conn.commit()
                state["sql_result"] = [{"success": True, "rows_affected": result.rowcount}]
                msg = f"Database operation completed. Rows affected: {result.rowcount}."
            else:
                # Select queries
                columns = result.keys()
                rows = result.fetchall()
                
                # Convert results to list of dicts, ensuring JSON-compatible datatypes
                data = []
                for row in rows:
                    row_dict = {}
                    for col, val in zip(columns, row):
                        # Convert date, time, and numeric types to string/float
                        if hasattr(val, "isoformat"):
                            row_dict[col] = val.isoformat()
                        elif hasattr(val, "to_eng_string"): # Decimal
                            row_dict[col] = float(val)
                        else:
                            row_dict[col] = val
                    data.append(row_dict)
                
                state["sql_result"] = data
                msg = f"Retrieved {len(data)} rows from database."
                
    except Exception as e:
        logger.error(f"SQL Tool Execution Error: {e}")
        state["sql_result"] = [{"error": str(e)}]
        msg = f"Execution error: {str(e)}"
        
    _log_tool(state, "Completed", msg)
    return state

def _log_tool(state: AgentState, status: str, message: str):
    if "agent_log" not in state or state["agent_log"] is None:
        state["agent_log"] = []
    state["agent_log"].append({
        "agent": "SQL Tool",
        "status": status,
        "message": message
    })
