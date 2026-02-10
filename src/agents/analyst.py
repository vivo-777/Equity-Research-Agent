import os
from langchain_groq import ChatGroq # type: ignore
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from src.agents.state import AgentState

# Initialize LLM
# We use Llama 3 70B for high-quality reasoning
llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.3-70b-versatile",
    temperature=0.2 # Low temperature = more factual/analytical
)

def analyst_node(state: AgentState):
    """
    The 'Brain' of the operation.
    Reads structured data and writes a draft analysis.
    """
    ticker = state["ticker"]
    prices = state["market_data"]
    techs = state["technicals"]
    news = state["news"]
    
    print(f"--- ANALYST ANALYZING: {ticker} ---")
    
    # 1. Construct the Context
    # We turn the complex dictionaries into a readable string for the LLM
    context = f"""
    TICKER: {ticker}
    
    --- MARKET DATA ---
    Price: ${prices.get('current_price', 'N/A')}
    Market Cap: {prices.get('market_cap', 'N/A')}
    P/E Ratio: {prices.get('pe_ratio', 'N/A')}
    Volatility: {prices.get('volatility_30d', 'N/A')}%
    
    --- TECHNICAL ANALYSIS ---
    RSI: {techs.get('momentum', {}).get('rsi', {}).get('value', 'N/A')} ({techs.get('momentum', {}).get('rsi', {}).get('signal', 'N/A')})
    MACD: {techs.get('trend', {}).get('macd', {}).get('trend', 'N/A')}
    Overall Signal: {techs.get('overall_signal', {}).get('signal', 'Unknown')}
    Confidence: {techs.get('overall_signal', {}).get('confidence', '0%')}
    
    --- RECENT NEWS ---
    """
    
    # Add top 3 news headlines
    for i, article in enumerate(news[:3]):
        context += f"{i+1}. {article.get('title', 'No Title')} (Source: {article.get('source', 'Unknown')})\n"

    # 2. Define the Prompt
    system_prompt = """You are a Senior Equity Analyst at a top-tier hedge fund. 
    Your job is to write a comprehensive investment memo based STRICTLY on the provided data.
    
    Structure your report as follows:
    1. **Executive Summary**: Buy/Sell/Hold recommendation with a strict confidence score.
    2. **Fundamental Analysis**: Valuation (P/E) and market position.
    3. **Technical Analysis**: Price action, RSI, and MACD trends.
    4. **Sentiment Analysis**: Summary of recent news and its potential impact.
    5. **Risk Factors**: What could go wrong?
    
    Tone: Professional, objective, and data-driven. 
    Do not hallucinate data. If data is missing, state it."""

    human_message = f"Here is the latest data for {ticker}. Write the analysis.\n\nData:\n{context}"
    
    # 3. Call the LLM
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_message)
    ]
    
    response = llm.invoke(messages)
    
    # 4. Return the Draft
    return {
        "analyst_draft": response.content,
        "recommendation": techs.get('overall_signal', {}).get('signal', 'Hold') # We stick to the math for the official tag
    }