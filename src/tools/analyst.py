import os
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from src.agents.state import AgentState


llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.3-70b-versatile",
    temperature=0.2 
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
    
  
    context = f"""
    TICKER: {ticker}
    
    --- MARKET DATA & FUNDAMENTALS ---
    Current Price: ${prices.get('current_price', 'N/A')}
    Market Cap: {prices.get('market_cap', 'N/A')}
    P/E Ratio: {prices.get('pe_ratio', 'N/A')}
    Forward P/E: {prices.get('forward_pe', 'N/A')}
    
    Revenue Growth: {prices.get('revenue_growth', 'N/A')}
    Profit Margins: {prices.get('profit_margins', 'N/A')}
    Debt to Equity: {prices.get('debt_to_equity', 'N/A')}
    
    --- TECHNICAL ANALYSIS ---
    Signal: {techs.get('overall_signal', {}).get('signal', 'Unknown')}
    Confidence: {techs.get('overall_signal', {}).get('confidence', '0%')}
    
    --- RECENT NEWS ---
    """
    

    if isinstance(news, list):
        for i, article in enumerate(news[:5]):
            title = article.get('title', 'No Title')
            url = article.get('url', 'No URL')
            context += f"\nArticle {i+1}: {title}\nSource: {url}\n"

    system_prompt = """You are a veteran Hedge Fund Portfolio Manager.
    
    ### INSTRUCTIONS:
    1. **BE DECISIVE:** You must output a distinct signal: BUY, SELL, or HOLD. 
    2. **USE THE DATA:** Cite the P/E ratio, Margins, and Debt data provided.
    3. **CONFIDENCE:** Provide a confidence score (0-100%). Scores below 50% are unacceptable.
    4. **FORMAT:** Use a professional Wall Street Memo format.
    """

    human_message = f"Here is the latest data for {ticker}. Write the analysis.\n\nData Context:\n{context}"

    messages = [SystemMessage(content=system_prompt), HumanMessage(content=human_message)]
    response = llm.invoke(messages)
    
    return {
        "analyst_draft": response.content,
        "recommendation": techs.get('overall_signal', {}).get('signal', 'Hold')
    }
