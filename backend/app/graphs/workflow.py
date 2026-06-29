from langgraph.graph import StateGraph, END
from app.graphs.state import AgentState
from app.agents.guardrail import run_guardrail_agent
from app.agents.supervisor import run_supervisor_agent
from app.agents.sql_agent import run_sql_agent
from app.agents.validator import run_validator_agent
from app.agents.response import run_response_agent
from app.tools.sql_tool import execute_sql_tool
from app.tools.rag_tool import run_rag_tool
from app.tools.memory_tool import run_memory_tool

def build_workflow():
    workflow = StateGraph(AgentState)

    # 1. Define nodes
    workflow.add_node("guardrail", run_guardrail_agent)
    workflow.add_node("supervisor", run_supervisor_agent)
    workflow.add_node("sql_agent", run_sql_agent)
    workflow.add_node("validator", run_validator_agent)
    workflow.add_node("sql_execute", execute_sql_tool)
    workflow.add_node("rag_tool", run_rag_tool)
    workflow.add_node("memory_tool", run_memory_tool)
    workflow.add_node("response_gen", run_response_agent)

    # 2. Set Entry point
    workflow.set_entry_point("guardrail")

    # 3. Define transitions
    workflow.add_edge("guardrail", "supervisor")

    # Conditional routing after Supervisor
    def supervisor_router(state: AgentState):
        route = state.get("route", "memory")
        if route == "blocked":
            return "response_gen"
        elif route == "sql":
            return "sql_agent"
        elif route == "rag":
            return "rag_tool"
        else:
            return "memory_tool"

    workflow.add_conditional_edges(
        "supervisor",
        supervisor_router,
        {
            "response_gen": "response_gen",
            "sql_agent": "sql_agent",
            "rag_tool": "rag_tool",
            "memory_tool": "memory_tool"
        }
    )

    # SQL Agent transition to Validator
    workflow.add_edge("sql_agent", "validator")

    # Conditional routing after Validator (Self-Correction Loop)
    def validator_router(state: AgentState):
        if state.get("sql_valid", False):
            return "sql_execute"
        
        # Limit loops to avoid infinite execution
        if state.get("sql_validation_attempts", 0) < 3:
            return "sql_agent"
        
        return "response_gen"

    workflow.add_conditional_edges(
        "validator",
        validator_router,
        {
            "sql_execute": "sql_execute",
            "sql_agent": "sql_agent",
            "response_gen": "response_gen"
        }
    )

    # Rejoin at Response Gen
    workflow.add_edge("sql_execute", "response_gen")
    workflow.add_edge("rag_tool", "response_gen")
    workflow.add_edge("memory_tool", "response_gen")

    # Final Node
    workflow.add_edge("response_gen", END)

    # Compile the graph
    return workflow.compile()

# Compile single app graph
app_workflow = build_workflow()
