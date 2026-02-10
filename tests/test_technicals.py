import sys
import os

# Fix path to allow importing from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.state import AgentState
from src.agents.nodes import market_data_node, technical_analysis_node

def test_chain():
    print("--- STARTING TECHNICAL ANALYSIS TEST CHAIN ---")

    # 1. Initialize State with Placeholder Values
    state: AgentState = {
        "ticker": "NVDA", # Nvidia
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
    
    # --- STEP 1: MARKET DATA NODE ---
    print("\nStep 1: Running Market Data Node...")
    market_update = market_data_node(state)
    
    if market_update:
        state.update(market_update) # type: ignore
    else:
        print("❌ Market Data Node returned no data.")
        return

    # --- STEP 2: TECHNICAL ANALYSIS NODE ---
    print("\nStep 2: Running Technical Analysis Node...")
    tech_update = technical_analysis_node(state)
    
    if tech_update:
        state.update(tech_update) # type: ignore
    
    # --- STEP 3: DISPLAY RESULTS ---
    # We access the 'technicals' key from the updated state
    techs = state.get('technicals', {})
    
    if not techs or "error" in techs:
        print(f"❌ Technical analysis failed: {techs.get('error')}")
        return

    print(f"\n✅ Technical Analysis Complete!")
    
    # 1. Momentum (RSI)
    if 'momentum' in techs:
        print(f"\n📊 Momentum:")
        print(f"   RSI: {techs['momentum']['rsi']['value']} ({techs['momentum']['rsi']['signal']})")
        print(f"   Stoch K: {techs['momentum']['stoch']['k']}")
    
    # 2. Trend (MACD & ADX)
    if 'trend' in techs:
        print(f"\n📈 Trend:")
        print(f"   MACD Trend: {techs['trend']['macd']['trend']}")
        print(f"   ADX Strength: {techs['trend']['adx']['value']} ({techs['trend']['adx']['strength']})")

    # 3. Overall Signal
    if 'overall_signal' in techs:
        signal = techs['overall_signal']
        print(f"\n🎯 Overall Signal:")
        print(f"   Action: {signal['signal'].upper()}")
        print(f"   Confidence: {signal['confidence']}")
        print(f"   Reasoning: {signal['reasoning']}")

if __name__ == "__main__":
    test_chain()