def stock_strategy(data):
    """
    Combines RSI, Moving Averages (SMA/EMA), MACD, and Bollinger Bands 
    to output a reliable stock trading signal (STRONG BUY, BUY, HOLD, SELL).
    """
    if len(data) < 20 or "RSI" not in data.columns or data["RSI"].isna().iloc[-1]:
        return "HOLD"
        
    latest = data.iloc[-1]
    
    rsi = latest["RSI"]
    close = latest["Close"]
    sma_20 = latest["SMA_20"]
    ema_20 = latest["EMA_20"]
    macd = latest["MACD"]
    macd_signal = latest["MACD_Signal"]
    bb_high = latest["BB_High"]
    bb_low = latest["BB_Low"]
    
    score = 0
    
    # 1. RSI Signals
    if rsi < 30:
        score += 3  # Oversold (Strong Bullish)
    elif rsi < 40:
        score += 1  # Moderate Oversold
    elif rsi > 70:
        score -= 3  # Overbought (Strong Bearish)
    elif rsi > 60:
        score -= 1  # Moderate Overbought
        
    # 2. Moving Averages
    if close > sma_20:
        score += 1
    else:
        score -= 1
        
    if close > ema_20:
        score += 1
    else:
        score -= 1
        
    # 3. MACD
    if macd > macd_signal:
        score += 2  # Bullish trend
    else:
        score -= 2  # Bearish trend
        
    # 4. Bollinger Bands
    if close < bb_low:
        score += 2  # Price below lower band (Oversold rebound likely)
    elif close > bb_high:
        score -= 2  # Price above upper band (Overbought resistance likely)
        
    # Translate Score to Signals
    if score >= 4:
        return "STRONG BUY"
    elif score >= 1:
        return "BUY"
    elif score <= -4:
        return "SELL"
    else:
        return "HOLD"