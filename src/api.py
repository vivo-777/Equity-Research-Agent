# src/api.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.main import app as graph_app  # Import your LangGraph agent
import uvicorn

# 1. Define Input Schema (What the API expects)
class AnalysisRequest(BaseModel):
    ticker: str
    max_revisions: int = 2

# 2. Initialize FastAPI
api = FastAPI(title="Hedge Fund Agent API", version="1.0")

@api.get("/")
def health_check():
    return {"status": "active", "model": "Llama-3.3-70b"}

@api.post("/analyze")
async def run_analysis(request: AnalysisRequest):
    """
    Triggers the LangGraph workflow for a specific ticker.
    """
    try:
        # Initialize the state as we did in the dashboard
        initial_state = {
            "ticker": request.ticker,
            "max_revisions": request.max_revisions,
            "revision_number": 0,
            "market_data": {},
            "technicals": {},
            "news": [],
            "analyst_draft": "",
            "critique": "",
            "final_report": "",
            "errors": []
        }
        
        # Run the graph (this might take 10-20 seconds)
        result = await graph_app.ainvoke(initial_state)
        
        # Return only what the frontend needs
        return {
            "ticker": result["ticker"],
            "current_price": result["market_data"].get("current_price"),
            "analyst_draft": result["analyst_draft"],
            "critique": result["critique"],
            "news": result["news"][:3], # Top 3 headlines
            "technicals": result["technicals"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("src.api:api", host="0.0.0.0", port=8000, reload=True)