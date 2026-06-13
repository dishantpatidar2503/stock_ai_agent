from langchain_core.tools import tool
import yfinance as yf

from stock_data import get_stock_data, get_live_quote, get_company_info
from indicators import add_indicators
from strategy import stock_strategy

@tool
def get_live_stock_quote(symbol: str) -> str:
    """
    Get the live current price, open, high, low, volume, and daily percentage change for a stock.
    Use this when the user asks for the current price or today's price movement.
    """
    try:
        quote = get_live_quote(symbol)
        return f"""
Live Quote for {symbol}:
- Current Price: ₹{quote['price']:.2f}
- Open: ₹{quote['open']:.2f}
- High: ₹{quote['high']:.2f}
- Low: ₹{quote['low']:.2f}
- Volume: {quote['volume']:,}
- Daily Change: ₹{quote['change']:.2f} ({quote['pct_change']:.2f}%)
"""
    except Exception as e:
        return f"Error fetching live quote for {symbol}: {str(e)}"

@tool
def fundamental_analysis_tool(symbol: str) -> str:
    """
    Fetch fundamental analysis metrics (P/E ratio, P/B ratio, Market Cap, Dividend Yield, and Company Profile/Summary).
    Use this when the user asks about the company's valuation, financials, or background.
    """
    try:
        info = get_company_info(symbol)
        mcap = info['market_cap']
        if mcap:
            if mcap >= 1e12:
                mcap_str = f"₹{mcap/1e12:.2f} Lakh Crore"
            elif mcap >= 1e7:
                mcap_str = f"₹{mcap/1e7:.2f} Cr"
            else:
                mcap_str = f"₹{mcap:,}"
        else:
            mcap_str = "N/A"
            
        return f"""
Fundamentals for {info['name']} ({symbol}):
- Market Capitalization: {mcap_str}
- Trailing P/E Ratio: {f"{info['pe_ratio']:.2f}" if info['pe_ratio'] else "N/A"}
- Price-to-Book (P/B) Ratio: {f"{info['pb_ratio']:.2f}" if info['pb_ratio'] else "N/A"}
- Dividend Yield: {f"{info['dividend_yield']:.2f}%" if info['dividend_yield'] is not None else "N/A"}
- 52-Week Range: ₹{info['year_low']:.2f} - ₹{info['year_high']:.2f} (if available)

Company Profile:
{info['summary'][:500]}...
"""
    except Exception as e:
        return f"Error performing fundamental analysis for {symbol}: {str(e)}"

@tool
def technical_analysis_tool(symbol: str) -> str:
    """
    Run technical analysis report on a stock including RSI, SMA, EMA, MACD, and Bollinger Bands.
    Use this when the user asks for technical indicators, moving averages, or trend directions.
    """
    try:
        data = get_stock_data(symbol)
        data = add_indicators(data)
        latest = data.iloc[-1]
        
        return f"""
Technical Indicators for {symbol}:
- Close Price: ₹{latest['Close']:.2f}
- Relative Strength Index (RSI): {latest['RSI']:.2f} (Values below 30 indicate oversold; above 70 indicate overbought)
- SMA 20 (Simple Moving Average): ₹{latest['SMA_20']:.2f}
- EMA 20 (Exponential Moving Average): ₹{latest['EMA_20']:.2f}
- MACD Line: {latest['MACD']:.2f} | Signal Line: {latest['MACD_Signal']:.2f} | Diff: {latest['MACD_Diff']:.2f}
- Bollinger Bands: High: ₹{latest['BB_High']:.2f} | Mid (SMA 20): ₹{latest['BB_Mid']:.2f} | Low: ₹{latest['BB_Low']:.2f}
"""
    except Exception as e:
        return f"Error performing technical analysis for {symbol}: {str(e)}"

@tool
def stock_advisor(symbol: str) -> str:
    """
    Analyze a stock comprehensively (technical indicators + strategy signals) and return a buying/selling recommendation (STRONG BUY, BUY, HOLD, SELL) with brief analysis.
    Use this when the user asks whether they should buy, sell, or hold a stock.
    """
    try:
        data = get_stock_data(symbol)
        data = add_indicators(data)
        signal = stock_strategy(data)
        latest = data.iloc[-1]
        
        return f"""
AI Recommendation for {symbol}:
- Recommendation: {signal}
- Current Close Price: ₹{latest['Close']:.2f}
- RSI: {latest['RSI']:.2f}
- SMA 20: ₹{latest['SMA_20']:.2f}
- MACD Line vs Signal: {latest['MACD']:.2f} / {latest['MACD_Signal']:.2f}
- Bollinger Band Lower/Upper: ₹{latest['BB_Low']:.2f} / ₹{latest['BB_High']:.2f}
"""
    except Exception as e:
        return f"Error analyzing stock: {str(e)}"

@tool
def get_recent_stock_news(symbol: str) -> str:
    """
    Fetch the latest market news, publisher names, and links related to a specific stock.
    Use this when the user asks for news, announcements, or updates about a stock.
    """
    try:
        stock = yf.Ticker(symbol)
        news = stock.news
        if not news:
            return f"No recent news articles found for {symbol}."
        
        articles = []
        for i, item in enumerate(news[:5]):
            title = item.get("title", "No Title")
            publisher = item.get("publisher", "N/A")
            link = item.get("link", "#")
            articles.append(f"{i+1}. **{title}**\n   *Publisher*: {publisher}\n   *Link*: {link}")
            
        return f"Latest News for {symbol}:\n\n" + "\n\n".join(articles)
    except Exception as e:
        return f"Error fetching news for {symbol}: {str(e)}"