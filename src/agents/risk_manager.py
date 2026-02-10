import os
from langchain_groq import ChatGroq # type: ignore
from langchain_core.messages import SystemMessage, HumanMessage
from src.agents.state import AgentState

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.3-70b-versatile",
    temperature=0.0 # Strict and analytical
)

def risk_manager_node(state: AgentState):
    """
    Reviews the Analyst's draft for logical inconsistencies or hallucinations.
    Decides if the report is safe to publish or needs revision.
    """
    print("--- RISK MANAGER REVIEWING DRAFT ---")
    
    draft = state["analyst_draft"]
    technicals = state["technicals"]
    prices = state["market_data"]
    
    # 1. Construct Context
    # We explicitly highlight the technical signals to ensure the LLM checks them
    tech_signal = technicals.get('overall_signal', {}).get('signal', 'Unknown')
    rsi = technicals.get('momentum', {}).get('rsi', {}).get('value', 'N/A')
    
    system_prompt = f"""You are a Risk Manager at a hedge fund. 
    Your job is to validate the Analyst's investment memo.
    
    HARD RULES:
    1. If the Analyst recommends 'BUY' but RSI is > 70 (Overbought), REJECT it.
    2. If the Analyst recommends 'SELL' but RSI is < 30 (Oversold), REJECT it.
    3. If the Analyst ignores the 'Overall Signal' ({tech_signal}), REJECT it.
    4. If the Confidence Score is low (< 50%) but the tone is aggressive, REJECT it.
    
    Output strictly in this format:
    DECISION: [APPROVE or REJECT]
    FEEDBACK: [One sentence explaining why]
    """
    
    human_message = f"""Here is the Analyst's Draft:\n\n{draft}\n\n
    Market Data:\nPrice: {prices.get('current_price')}\nRSI: {rsi}\nOverall Tech Signal: {tech_signal}"""
    
    # 2. Call LLM
    response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=human_message)])
    result = response.content
    
    # 3. Parse Output
    decision = "APPROVE"
    feedback = "LGTM"
    
    if "REJECT" in result:
        decision = "REJECT"
        feedback = result.split("FEEDBACK:")[-1].strip()
    
    print(f"Risk Manager Decision: {decision}")
    
    return {
        "critique": feedback,
        "revision_number": state.get("revision_number", 0) + 1
    }

    