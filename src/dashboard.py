import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# --- IMPORT THE AGENT DIRECTLY (Monolith Architecture) ---
try:
    from src.main import app
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from src.main import app

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Equity Research", layout="wide")
st.title("🤖 AI Equity Research Agent")

# --- 2. SIDEBAR ---
with st.sidebar:
    st.header("Trade Settings")
    ticker = st.text_input("Ticker Symbol", value="NVDA").upper()
    max_revisions = st.number_input("Max Risk Revisions", min_value=1, max_value=5, value=2)
    run_btn = st.button("Generate Analysis", type="primary")

# --- 3. MAIN LOGIC ---
if run_btn:
    with st.spinner(f"Running autonomous agents for {ticker}..."):
        try:
            # --- EXECUTION ---
            initial_state = {
                "ticker": ticker, 
                "max_revisions": max_revisions,
                "revision_count": 0
            }
            final_state = app.invoke(initial_state)
            
            # --- 4. PARSE DATA ---
            market_data = final_state.get("market_data", {})
            technicals = final_state.get("technicals", {})
            news = final_state.get("news", [])
            analyst_draft = final_state.get("analyst_draft", "No report generated.")
            critique = final_state.get("critique")
            
            col1, col2, col3 = st.columns(3)
            current_price = market_data.get("current_price", "N/A")
            signal = technicals.get('overall_signal', {}).get('signal', 'Neutral')
            
            col1.metric("Ticker", ticker)
            col2.metric("Current Price", f"${current_price}")
            col3.metric("Analyst Decision", signal)

            st.subheader(f"{ticker} Price Action (6 Months)")
            
            if "history_df" in market_data and not market_data["history_df"].empty:
                df = market_data["history_df"]
                fig = go.Figure(data=[go.Candlestick(
                    x=df.index,
                    open=df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Close']
                )])
                fig.update_layout(
                    xaxis_rangeslider_visible=False,
                    template="plotly_dark",
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Price history data not available for charting.")

            tab1, tab2, tab3 = st.tabs(["📝 Research Report", "📊 Fundamental Data", "🧠 Agent Logic"])
            
            with tab1:
                st.markdown("### Investment Memo")
                st.markdown(analyst_draft)
            
            with tab2:
                st.subheader("Financial Metrics")
                metrics_df = pd.DataFrame([
                    {"Metric": k, "Value": v} 
                    for k, v in market_data.items() 
                    if k != "history_df"
                ])
                st.table(metrics_df)
                
                st.subheader("Recent News")
                if news:
                    for article in news[:5]:
                        st.markdown(f"- **{article.get('title')}** [Read Source]({article.get('url')})")
                    
            with tab3:
                st.subheader("Risk Management Critique")
                if critique:
                    st.warning(f"Risk Manager Feedback:\n\n{critique}")
                else:
                    st.success("Risk Manager approved the report immediately.")
                    
                st.subheader("Technical Indicators")
                st.json(technicals)

        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")
