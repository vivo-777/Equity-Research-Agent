import sys
import os

# Fix path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.state import AgentState
from src.agents.nodes import market_data_node, technical_analysis_node, news_gatherer_node
from src.agents.analyst import analyst_node

def test_full_flow():
    print("--- STARTING FULL ANALYST FLOW ---")
    
    # 1. Initialize
    state: AgentState = {
        "ticker": "TSLA",
        "market_data": {},     
        "price_history": None, 
        "technicals": {},      
        "news": [],            
        "recommendation": "",  
        "target_price": "",
        "analyst_draft": "",
        "critique": "",
        "revision_number": 0,
        "max_revisions": 3,
        "final_report": "",
        "errors": []
    }
    
    # 2. Gather Data (Simulating the Graph)
    print("1. Gathering Market Data...")
    state.update(market_data_node(state)) # type: ignore
    
    print("2. Analyzing Technicals...")
    state.update(technical_analysis_node(state)) # type: ignore
    
    print("3. Reading News...")
    state.update(news_gatherer_node(state)) # type: ignore
    
    # 3. Run the Brain
    print("4. 🧠 Running Analyst LLM...")
    result = analyst_node(state)
    
    print("\n\n=== FINAL REPORT DRAFT ===\n")
    print(result["analyst_draft"])

if __name__ == "__main__":
    test_full_flow()