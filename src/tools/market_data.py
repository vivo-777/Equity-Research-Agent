import yfinance as yf
import pandas as pd
from typing import Dict, Any

def fetch_market_data(ticker: str) -> Dict[str, Any]:
    """
    Fetch comprehensive market data for a given stock ticker.
    Returns a dictionary with summary metrics AND the raw history dataframe.
    """
    try:
        # Clean ticker input
        ticker = ticker.upper().strip()
        stock = yf.Ticker(ticker)
        
        # 1. Fetch Info (Metadata)
        # Note: .info can be slow or flaky, so we default to empty dict if it fails
        try:
            info = stock.info
        except:
            info = {}

        # 2. Fetch History (Needed for Volatility & Technicals)
        # We fetch 6mo to ensure we have enough data for MACD (26 periods) + RSI (14 periods)
        hist = stock.history(period="6mo") 
        
        if hist.empty:
            return {"error": f"No price data available for ticker: {ticker}"}
            
        # 3. Calculate Derived Metrics
        current_price = hist['Close'].iloc[-1]
        prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
        
        # Price Change
        price_change = current_price - prev_close
        price_change_pct = (price_change / prev_close) * 100 if prev_close else 0
        
        # Volume Ratio (Current vs 30-day Avg)
        # Check if we have enough data for 30d avg, else take whatever mean we have
        avg_volume_30d = hist['Volume'].iloc[-30:].mean() if len(hist) >= 30 else hist['Volume'].mean()
        current_volume = hist['Volume'].iloc[-1]
        volume_ratio = current_volume / avg_volume_30d if avg_volume_30d > 0 else 0
        
        # Volatility (30-day rolling std dev of percent change)
        if len(hist) >= 30:
            volatility = hist['Close'].pct_change().rolling(window=30).std().iloc[-1] * 100
        else:
            volatility = 0.0 # Not enough data
        
        # 4. Construct the Payload
        market_data = {
            "ticker": ticker,
            "company_name": info.get('longName', ticker),
            "sector": info.get('sector', 'Unknown'),
            "industry": info.get('industry', 'Unknown'),
            "current_price": round(current_price, 2),
            "price_change_percent": round(price_change_pct, 2),
            "volume_ratio": round(volume_ratio, 2),
            "market_cap": format_market_cap(info.get('marketCap', 0)),
            "pe_ratio": info.get('trailingPE', 'N/A'),
            "volatility_30d": round(volatility, 2) if pd.notnull(volatility) else "N/A",
            
            # HIDDEN FIELD: The raw dataframe for the Technical Analysis Node
            "history_df": hist 
        }
        
        return market_data

    except Exception as e:
        return {"error": f"Market data fetch failed: {str(e)}"}

def format_market_cap(val: float) -> str:
    """Helper to make huge numbers readable (e.g., 2.5T, 45B)"""
    if not val or val == "N/A": return "N/A"
    try:
        val = float(val)
    except:
        return str(val)
        
    if val >= 1e12: return f"${val/1e12:.2f}T"
    if val >= 1e9: return f"${val/1e9:.2f}B"
    if val >= 1e6: return f"${val/1e6:.2f}M"
    return f"${val:,.0f}"