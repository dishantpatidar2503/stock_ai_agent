from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph.message import add_messages
from langchain_core.messages import SystemMessage

from langgraph.graph import (
    StateGraph,
    START,
    END
)

from langgraph.prebuilt import (
    ToolNode,
    tools_condition
)

from llm import llm
from tools import (
    stock_advisor,
    get_live_stock_quote,
    fundamental_analysis_tool,
    technical_analysis_tool,
    get_recent_stock_news
)

# Bundle all stock-related tools
tools = [
    stock_advisor,
    get_live_stock_quote,
    fundamental_analysis_tool,
    technical_analysis_tool,
    get_recent_stock_news
]

llm_with_tools = llm.bind_tools(tools)

class State(TypedDict):
    messages: Annotated[list, add_messages]

SYSTEM_PROMPT = """You are a premium, highly intelligent Personal Stock AI Agent. 
Your goal is to help users analyze stocks, check live prices, understand company fundamentals and technicals, read news, and decide whether to BUY, SELL, or HOLD a stock.

Guidelines:
1. Always use the appropriate tool(s) to fetch data (quote, fundamentals, technicals, advisor, or news) before responding. Never hallucinate or guess stock prices or indicators.
2. For Indian stocks listed on NSE, the symbol needs to end with '.NS' (e.g., RELIANCE.NS, TCS.NS, TATAMOTORS.NS). If the user inputs a plain name like 'Reliance' or 'TCS', tell them that they should use the '.NS' suffix for NSE stocks, or check it by appending '.NS' automatically.
3. Provide advice with clear, structured bullet points. Explain technicals (RSI, MACD, Bollinger Bands) and fundamentals (PE, Market Cap) to justify your recommendation.
4. Respond in the user's language. If they query in Hindi/Hinglish (e.g. 'kaun sa stock buy karu', 'reliance ka price batao'), reply in helpful, easy-to-understand Hinglish/Hindi.
5. Add a short disclaimer that investing involves risk, and your advice is for informational and analysis purposes.
6. For market indices like NIFTY 50 (or Nifty), SENSEX, and BANK NIFTY (or Bank Nifty), map them to yfinance tickers ^NSEI, ^BSESN, and ^NSEBANK respectively when using tools.
"""

def chatbot(state: State):
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    return {
        "messages": [
            llm_with_tools.invoke(messages)
        ]
    }

builder = StateGraph(State)

builder.add_node("chatbot", chatbot)

builder.add_node(
    "tools",
    ToolNode(tools)
)

builder.add_edge(
    START,
    "chatbot"
)

builder.add_conditional_edges(
    "chatbot",
    tools_condition
)

builder.add_edge(
    "tools",
    "chatbot"
)

graph = builder.compile()