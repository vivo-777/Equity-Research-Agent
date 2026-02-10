from typing import TypedDict, Annotated, List, Dict, Any
import operator
class AgentState(TypedDict):

    ##input
    ticker: str # unquie stock id for the company 

    ##Data
    market_data: Dict[str, Any] #price, volume, Market cap
    technicals: Dict[str, Any]  # RSI, MACD, Trend
    news: List[Dict[str, Any]]  # List of news articles (Title, Content)
    price_history: Any

    #structured logic
    recommendation: str   #buy, sell, hold 
    target_price: str   #optional price targetted

    #Reasoning
    analyst_draft: str  #written by the analyst
    critique: str       #feedback from risk manager

    #contol 
    revision_number: int  #loop count
    max_revisions: int    #Maximum loop count 

    #output
    final_report: str           # The final, polished markdown report
    errors: Annotated[List[str], operator.add] # tool failures








