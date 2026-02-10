import sys
import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go # type: ignore

import sys
import os

# --- 1. ROBUST PATH SETUP ---
# Get the absolute path to the project root folder
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))

# Add the project root to Python's system path if it's not there
if project_root not in sys.path:
    sys.path.append(project_root)

# NOW we can import from src
import streamlit as st
import plotly.graph_objects as go # type: ignore
# Use try-except to catch import errors and show them in the UI
try:
    from src.main import app 
except ImportError as e:
    st.error(f"Error importing the agent: {e}")
    st.stop()
except Exception as e:
    st.error(f"Unexpected error: {e}")
    st.stop()

# ... (The rest of your code remains the same from "--- 2. PAGE CONFIG ---")

# --- 1. SETUP PATH ---
# Allow importing from the root folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the graph we built in main.py
from src.main import app 

# --- 2. PAGE CONFIG ---
st.set_page_config(
    page_title="Autonomous Equity Analyst",
    page_icon="📈",
    layout="wide"
)

st.title("🤖 Autonomous Equity Analyst")
st.markdown("### Powered by Llama 3.3 & LangGraph")

# --- 3. SIDEBAR INPUTS ---
with st.sidebar:
    st.header("Configuration")
    ticker = st.text_input("Enter Stock Ticker:", value="NVDA").upper()
    
    # Optional: Let user tweak settings
    max_revisions = st.number_input("Max Revisions (Risk Loop):", min_value=1, max_value=5, value=2)
    
    run_btn = st.button("Generate Analysis", type="primary")

# --- 4. MAIN LOGIC ---
if run_btn:
    with st.spinner(f"Gathering data and analyzing {ticker}... (This may take 10-20 seconds)"):
        
        # A. Initialize State
        initial_state = {
            "ticker": ticker,
            "revision_number": 0,
            "max_revisions": max_revisions,
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
        
        # B. Run the Graph
        # We use .invoke() to run the entire pipeline
        result = app.invoke(initial_state)
        
        # C. Display Results
        
        # --- Top Level Metrics ---
        prices = result.get("market_data", {})
        col1, col2, col3, col4 = st.columns(4)
        
        if prices:
            col1.metric("Current Price", f"${prices.get('current_price', 'N/A')}")
            col2.metric("Market Cap", prices.get('market_cap', 'N/A'))
            col3.metric("P/E Ratio", prices.get('pe_ratio', 'N/A'))
            
            # Show the "Risk Manager" Decision (Revision Count)
            revs = result.get("revision_number", 0)
            col4.metric("Risk Reviews Triggered", f"{revs}/{max_revisions}", 
                        delta_color="off" if revs == 0 else "inverse")
        else:
            st.error("Failed to fetch market data.")

        # --- Tabs for Detailed View ---
        tab1, tab2, tab3 = st.tabs(["📝 Investment Memo", "📊 Price Chart", "🧠 Agent Logic"])
        
        with tab1:
            st.markdown("---")
            # The final draft from the analyst
            report = result.get("analyst_draft", "No report generated.")
            st.markdown(report)
            
        with tab2:
            st.subheader(f"{ticker} Price History (6 Months)")
            history_df = result.get("price_history")
            
            if history_df is not None and not history_df.empty:
                # Create interactive Plotly chart
                fig = go.Figure()
                fig.add_trace(go.Candlestick(
                    x=history_df.index,
                    open=history_df['Open'],
                    high=history_df['High'],
                    low=history_df['Low'],
                    close=history_df['Close'],
                    name='Price'
                ))
                fig.update_layout(xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No price history available to plot.")
                
        with tab3:
            st.subheader("Under the Hood")
            
            # 1. Show the critique if any
            critique = result.get("critique")
            if critique:
                st.warning(f"⚠️ Risk Manager Feedback during loop:\n\n'{critique}'")
            else:
                st.success("✅ Risk Manager approved the draft on the first try.")
            
            # 2. Show Technicals
            st.json(result.get("technicals", {}))
            
            # 3. Show News
            st.subheader("News Sources Used")
            for article in result.get("news", []):
                st.markdown(f"- [{article['title']}]({article['url']})")