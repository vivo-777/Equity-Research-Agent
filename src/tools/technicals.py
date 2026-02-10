import pandas as pd
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.trend import MACD, ADXIndicator, SMAIndicator
from ta.volatility import BollingerBands

def calculate_technicals(df: pd.DataFrame) -> dict:
    """
    Advanced technical analysis with nested structure and signal scoring.
    """
    try:
        if df.empty or len(df) < 20:
            return {"error": "Not enough data for technical analysis"}

        # Use a copy to avoid SettingWithCopy warnings
        df = df.copy()
        current_price = df['Close'].iloc[-1]

        # --- 1. MOMENTUM INDICATORS ---
        # RSI
        rsi = RSIIndicator(close=df['Close'], window=14).rsi().iloc[-1]
        rsi_signal = "Overbought" if rsi > 70 else "Oversold" if rsi < 30 else "Neutral"
        
        # Stochastic
        stoch = StochasticOscillator(high=df['High'], low=df['Low'], close=df['Close'], window=14, smooth_window=3)
        stoch_k = stoch.stoch().iloc[-1]
        stoch_signal = "Overbought" if stoch_k > 80 else "Oversold" if stoch_k < 20 else "Neutral"

        # --- 2. TREND INDICATORS ---
        # MACD
        macd = MACD(close=df['Close'])
        macd_line = macd.macd().iloc[-1]
        macd_signal_line = macd.macd_signal().iloc[-1]
        macd_trend = "Bullish" if macd_line > macd_signal_line else "Bearish"
        
        # ADX (Trend Strength)
        adx = ADXIndicator(high=df['High'], low=df['Low'], close=df['Close'], window=14)
        adx_val = adx.adx().iloc[-1]
        trend_strength = "Strong" if adx_val > 25 else "Weak"

        # SMA Crossover (Golden/Death Cross check)
        sma_50 = SMAIndicator(close=df['Close'], window=50).sma_indicator().iloc[-1]
        sma_200 = SMAIndicator(close=df['Close'], window=200).sma_indicator().iloc[-1]
        sma_signal = "Bullish" if sma_50 > sma_200 else "Bearish"

        # --- 3. VOLATILITY ---
        bb = BollingerBands(close=df['Close'], window=20, window_dev=2)
        bb_upper = bb.bollinger_hband().iloc[-1]
        bb_lower = bb.bollinger_lband().iloc[-1]
        bb_signal = "Above Upper" if current_price > bb_upper else "Below Lower" if current_price < bb_lower else "Inside Bands"

        # --- 4. SCORING ALGORITHM ---
        score = 0
        reasoning = []
        
        # Bullish factors
        if rsi < 30: score += 1; reasoning.append("RSI is Oversold (Buy signal)")
        if macd_trend == "Bullish": score += 1; reasoning.append("MACD is Bullish")
        if sma_signal == "Bullish": score += 1; reasoning.append("Price above SMA support")
        if current_price < bb_lower: score += 1; reasoning.append("Price below Bollinger Band (Oversold)")
        
        # Bearish factors
        if rsi > 70: score -= 1; reasoning.append("RSI is Overbought (Sell signal)")
        if macd_trend == "Bearish": score -= 1; reasoning.append("MACD is Bearish")
        if current_price > bb_upper: score -= 1; reasoning.append("Price above Bollinger Band (Overbought)")

        # Normalize score to signal
        final_signal = "Hold"
        if score >= 2: final_signal = "Buy"
        elif score <= -2: final_signal = "Sell"

        return {
            "success": True,
            "momentum": {
                "rsi": {"value": round(rsi, 2), "signal": rsi_signal},
                "stoch": {"k": round(stoch_k, 2), "signal": stoch_signal}
            },
            "trend": {
                "macd": {"value": round(macd_line, 4), "signal": round(macd_signal_line, 4), "trend": macd_trend},
                "adx": {"value": round(adx_val, 2), "strength": trend_strength},
                "sma": {"sma_50": round(sma_50, 2), "sma_200": round(sma_200, 2), "signal": sma_signal}
            },
            "volatility": {
                "bb_upper": round(bb_upper, 2),
                "bb_lower": round(bb_lower, 2),
                "signal": bb_signal
            },
            "overall_signal": {
                "signal": final_signal,
                "score": score,
                "confidence": f"{abs(score)/4*100:.0f}%", # Simple confidence metric
                "reasoning": reasoning
            }
        }

    except Exception as e:
        return {"error": str(e)}