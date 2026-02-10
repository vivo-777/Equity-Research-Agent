import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langgraph.graph import StateGraph, END # type: ignore
from src.agents.state import AgentState
from src.agents.nodes import market_data_node, technical_analysis_node, news_gatherer_node
from src.agents.analyst import analyst_node
from src.agents.risk_manager import risk_manager_node

def should_continue(state: AgentState):
    """
    The Conditional Logic:
    - If Risk Manager rejects AND we haven't hit max revisions -> Loop back to Analyst.
    - Else -> End.
    """
    critique = state.get("critique", "")
    revisions = state.get("revision_number", 0)
    max_revisions = state.get("max_revisions", 2)
    
    if "APPROVE" in critique or revisions >= max_revisions:
        return "end"
    else:
        return "revision"

# 1. Initialize Graph
workflow = StateGraph(AgentState)

# 2. Add Nodes
workflow.add_node("data_gatherer", market_data_node)
workflow.add_node("technicals", technical_analysis_node)
workflow.add_node("news", news_gatherer_node)
workflow.add_node("analyst", analyst_node)
workflow.add_node("risk_manager", risk_manager_node)

# 3. Define Edges (The Flow)
workflow.set_entry_point("data_gatherer")

# Parallel Fetching: After data_gatherer, run technicals and news in parallel? 
# For simplicity, we'll keep it linear first, but LangGraph supports parallel.
workflow.add_edge("data_gatherer", "technicals")
workflow.add_edge("technicals", "news")
workflow.add_edge("news", "analyst")
workflow.add_edge("analyst", "risk_manager")

# 4. Conditional Edge (The Loop)
workflow.add_conditional_edges(
    "risk_manager",
    should_continue,
    {
        "revision": "analyst", # Loop back!
        "end": END             # Finish
    }
)

# 5. Compile
app = workflow.compile()

# --- RUN IT ---
if __name__ == "__main__":
    print("--- STARTING HEDGE FUND AGENT ---")
    ticker = "NVDA"
    
    initial_state = {
        "ticker": ticker,
        "revision_number": 0,
        "max_revisions": 2,
        # Initialize other required fields to avoid validation errors
        "market_data": {},
        "price_history": None,
        "technicals": {},
        "news": [],
        "recommendation": "",
        "target_price": "",
        "analyst_draft": "",
        "critique": "",
        "final_report": "",
        "errors": []
    }
    
    result = app.invoke(initial_state)
    
    print("\n\n################################")
    print("FINAL REPORT")
    print("################################\n")
    print(result["analyst_draft"])