import sys
import os

# Fix path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.state import AgentState
from src.agents.nodes import news_gatherer_node

def test_news():
    print("--- STARTING NEWS TEST ---")
    
    # Initialize State
    state: AgentState = {
        "ticker": "AAPL", # Apple
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
    
    # Run the Node
    update = news_gatherer_node(state)
    
    if "errors" in update:
        print(f"❌ Error: {update['errors']}")
        return

    # Simulate State Merge
    state.update(update) # type: ignore
    
    # Print Results
    articles = state['news']
    print(f"\n✅ Found {len(articles)} articles for AAPL:\n")
    
    for i, article in enumerate(articles[:3]): # Print top 3
        print(f"{i+1}. {article['title']}")
        print(f"   URL: {article['url']}")
        print(f"   Preview: {article['content'][:100]}...\n")

if __name__ == "__main__":
    test_news()