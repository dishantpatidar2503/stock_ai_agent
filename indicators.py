import ta

def add_indicators(data):
    if len(data) < 20:
        # Avoid crashing on short data sets by initializing indicators to None
        data["RSI"] = 50.0
        data["SMA_20"] = data["Close"]
        data["EMA_20"] = data["Close"]
        data["MACD"] = 0.0
        data["MACD_Signal"] = 0.0
        data["BB_High"] = data["Close"]
        data["BB_Low"] = data["Close"]
        data["BB_Mid"] = data["Close"]
        return data

    data["RSI"] = ta.momentum.RSIIndicator(
        close=data["Close"]
    ).rsi()

    data["SMA_20"] = data["Close"].rolling(20).mean()
    data["EMA_20"] = data["Close"].ewm(span=20).mean()

    # Add MACD
    macd = ta.trend.MACD(close=data["Close"])
    data["MACD"] = macd.macd()
    data["MACD_Signal"] = macd.macd_signal()
    data["MACD_Diff"] = macd.macd_diff()

    # Add Bollinger Bands
    bb = ta.volatility.BollingerBands(close=data["Close"])
    data["BB_High"] = bb.bollinger_hband()
    data["BB_Low"] = bb.bollinger_lband()
    data["BB_Mid"] = bb.bollinger_mavg()

    return data