import streamlit as st
import plotly.graph_objects as go
import yfinance as yf
from langchain_core.messages import HumanMessage, AIMessage

from agent import graph
from stock_data import get_stock_data, get_live_quote, get_company_info, get_indices_data
from charts import candlestick_chart
from indicators import add_indicators
from strategy import stock_strategy

# --- PAGE SETUP ---
st.set_page_config(
    page_title="GrowwAI - Personal Stock AI Agent & Portfolio Dashboard",
    page_icon="📈",
    layout="wide"
)

# --- SESSION STATE INITIALIZATION ---
if "selected_stock" not in st.session_state:
    st.session_state.selected_stock = "RELIANCE.NS"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "holdings" not in st.session_state:
    # Prepopulate with sample holdings to showcase the feature immediately
    st.session_state.holdings = [
        {"symbol": "RELIANCE.NS", "quantity": 10, "buy_price": 2420.0},
        {"symbol": "TCS.NS", "quantity": 5, "buy_price": 3810.0},
        {"symbol": "TATAMOTORS.NS", "quantity": 25, "buy_price": 620.0}
    ]

# --- PREMIUM GROWW-LIKE STYLING ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

/* Global Font Override */
html, body, [class*="css"], .stMarkdown {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

/* Header styling */
.groww-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 15px 0px;
    border-bottom: 1px solid #f0f3f6;
    margin-bottom: 25px;
}
.groww-logo {
    font-size: 26px;
    font-weight: 800;
    color: #00d09c; /* Groww Green */
    display: flex;
    align-items: center;
    gap: 8px;
    letter-spacing: -0.5px;
}
.groww-logo span {
    color: #1e293b;
}

/* Cards & Badges styling */
.index-card {
    background: #ffffff;
    border-radius: 12px;
    padding: 16px 20px;
    border: 1px solid #eef2f6;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.01), 0 2px 4px -1px rgba(0,0,0,0.01);
    transition: all 0.2s ease;
}
.index-card:hover {
    box-shadow: 0 10px 15px -3px rgba(0,0,0,0.03);
    border-color: #00d09c;
}
.index-title {
    font-size: 13px;
    color: #64748b;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.index-value {
    font-size: 22px;
    font-weight: 800;
    color: #0f172a;
    margin-top: 6px;
}
.return-green {
    color: #00d09c !important;
    font-weight: 700;
}
.return-red {
    color: #ff5050 !important;
    font-weight: 700;
}

.popular-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 12px;
    text-align: center;
    box-shadow: 0 2px 4px rgba(0,0,0,0.01);
    transition: all 0.2s ease;
}
.popular-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 16px rgba(0,0,0,0.04);
    border-color: #00d09c;
}

/* Portfolio Summary UI */
.portfolio-metric-card {
    background: #ffffff;
    padding: 20px;
    border-radius: 16px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    text-align: left;
}
.portfolio-metric-title {
    font-size: 14px;
    color: #64748b;
    font-weight: 600;
}
.portfolio-metric-value {
    font-size: 28px;
    font-weight: 800;
    color: #0f172a;
    margin-top: 5px;
}

/* Custom Alert Badge styles */
.badge {
    padding: 6px 14px;
    border-radius: 50px;
    font-weight: 700;
    font-size: 14px;
    display: inline-block;
}
.badge-strong-buy {
    background-color: #e6fcf5;
    color: #00d09c;
    border: 1px solid #00d09c;
}
.badge-buy {
    background-color: #f0fdf4;
    color: #16a34a;
    border: 1px solid #16a34a;
}
.badge-hold {
    background-color: #fefce8;
    color: #ca8a04;
    border: 1px solid #ca8a04;
}
.badge-sell {
    background-color: #fff5f5;
    color: #ff5050;
    border: 1px solid #ff5050;
}

.table-row:hover {
    background-color: #f8fafc;
}
</style>
""", unsafe_allow_html=True)

# --- HEADER NAVIGATION ---
st.markdown("""
<div class="groww-header">
    <div class="groww-logo">
        📈 Dishant's<span>AI Agent</span>
    </div>
    <div style="background-color: #e6fcf5; color: #00d09c; padding: 6px 14px; border-radius: 20px; font-weight: 600; font-size: 12px; display: flex; align-items: center; gap: 6px;">
        <span style="width: 8px; height: 8px; background-color: #00d09c; border-radius: 50%; display: inline-block; animation: pulse 1.5s infinite;"></span>
        Live Analysis Active
    </div>
</div>
""", unsafe_allow_html=True)

# --- LIVE INDICES PANEL ---
indices_data = get_indices_data()
idx_cols = st.columns(3)
for idx, (name, quote) in enumerate(indices_data.items()):
    with idx_cols[idx]:
        price = quote["price"]
        change = quote["change"]
        pct = quote["pct_change"]
        
        color_class = "return-green" if change >= 0 else "return-red"
        arrow = "▲" if change >= 0 else "▼"
        
        st.markdown(f"""
        <div class="index-card">
            <div class="index-title">{name}</div>
            <div class="index-value">₹{price:,.2f}</div>
            <div style="font-size: 14px; margin-top: 4px;" class="{color_class}">
                {arrow} {abs(change):.2f} ({pct:+.2f}%)
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Interactive analysis button
        tickers = {
            "NIFTY 50": "^NSEI",
            "SENSEX": "^BSESN",
            "BANK NIFTY": "^NSEBANK"
        }
        if st.button(f"Analyze {name} 📊", key=f"btn_idx_{name}", use_container_width=True):
            st.session_state.selected_stock = tickers[name]
            st.rerun()

st.write("")  # Whitespace

# --- TAB LAYOUT (Explore, Holdings, AI Agent) ---
tab_explore, tab_portfolio, tab_ai_agent = st.tabs([
    "🔍 Explore & Live Analysis", 
    "💼 My Portfolio Tracker", 
    "🤖 Chat with AI Stock Agent"
])

# ==============================================================================
# TAB 1: EXPLORE & LIVE ANALYSIS
# ==============================================================================
with tab_explore:
    st.subheader("Recently Viewed & Popular Stocks")
    
    popular_stocks = [
        {"name": "Reliance Industries", "symbol": "RELIANCE.NS"},
        {"name": "TCS", "symbol": "TCS.NS"},
        {"name": "Infosys", "symbol": "INFY.NS"},
        {"name": "Tata Motors", "symbol": "TATAMOTORS.NS"},
        {"name": "Wipro Ltd", "symbol": "WIPRO.NS"},
        {"name": "Ola Electric", "symbol": "OLAELEC.NS"}
    ]
    
    pop_cols = st.columns(6)
    for idx, item in enumerate(popular_stocks):
        with pop_cols[idx]:
            try:
                # Fetch 2-day history for popular stocks return display
                quote = get_live_quote(item["symbol"])
                price = quote["price"]
                pct = quote["pct_change"]
                color_class = "return-green" if pct >= 0 else "return-red"
                sign = "+" if pct >= 0 else ""
                
                st.markdown(f"""
                <div class="popular-card">
                    <div style="font-size: 14px; font-weight: 700; color: #1e293b; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{item['name']}</div>
                    <div style="font-size: 11px; color: #64748b; margin-bottom: 6px;">{item['symbol']}</div>
                    <div style="font-size: 16px; font-weight: 800; color: #0f172a;">₹{price:,.2f}</div>
                    <div class="{color_class}" style="font-size: 12px; margin-top: 2px;">{sign}{pct:.2f}%</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Hidden button layer to handle clicks
                if st.button("Analyze", key=f"btn_pop_{item['symbol']}", use_container_width=True):
                    st.session_state.selected_stock = item["symbol"]
                    st.rerun()
            except Exception:
                st.markdown(f"""
                <div class="popular-card" style="opacity: 0.6;">
                    <div style="font-size: 14px; font-weight: 700; color: #1e293b;">{item['name']}</div>
                    <div style="font-size: 11px; color: #64748b;">{item['symbol']}</div>
                    <div style="font-size: 14px; color: #94a3b8; margin-top: 4px;">Offline</div>
                </div>
                """, unsafe_allow_html=True)

    st.write("---")
    
    # SEARCH CONTAINER
    st.subheader("Live Stock Analysis Terminal")
    search_col1, search_col2 = st.columns([3, 1])
    with search_col1:
        search_sym = st.text_input(
            "Enter NSE/BSE Symbol or US Ticker:", 
            value=st.session_state.selected_stock,
            placeholder="Examples: RELIANCE.NS, TCS.NS, TATAMOTORS.NS, AAPL, TSLA"
        )
    with search_col2:
        st.write(" ")
        st.write(" ")
        if st.button("Search & Analyze Stock", use_container_width=True, type="primary"):
            if search_sym:
                st.session_state.selected_stock = search_sym.strip().upper()
                st.rerun()
                
    st.markdown("""
    <div style="font-size: 12px; color: #64748b; margin-top: -10px; margin-bottom: 20px;">
        💡 <b>Tip</b>: Indian stocks require <b>.NS</b> suffix (NSE) or <b>.BO</b> (BSE) e.g., <b>TCS.NS</b>. Market indices require a leading <b>^</b> e.g. <b>^NSEI</b> (Nifty 50), <b>^BSESN</b> (Sensex), <b>^NSEBANK</b> (Bank Nifty). US stocks like <b>AAPL</b>, <b>TSLA</b> require no suffix.
    </div>
    """, unsafe_allow_html=True)

    # DYNAMIC PERFORMANCE & ANALYSIS SECTION
    active_symbol = st.session_state.selected_stock
    
    with st.spinner(f"Loading Live Analysis for {active_symbol}..."):
        try:
            # Fetch Stock Quote & Company Info
            quote = get_live_quote(active_symbol)
            info = get_company_info(active_symbol)
            
            # Currency formatting
            curr = "₹" if (".NS" in active_symbol or ".BO" in active_symbol or active_symbol.startswith("^")) else "$"
            
            # Setup columns for header metrics
            anal_col1, anal_col2, anal_col3, anal_col4 = st.columns([2, 1, 1, 1])
            with anal_col1:
                st.markdown(f"""
                <div style="margin-bottom: 15px;">
                    <h2 style="margin: 0; color: #0f172a; font-weight: 800;">{info['name']}</h2>
                    <span style="font-size: 14px; color: #64748b; font-weight: 600;">{active_symbol}</span>
                </div>
                """, unsafe_allow_html=True)
            with anal_col2:
                pct_val = quote['pct_change']
                col_c = "return-green" if pct_val >= 0 else "return-red"
                sign = "+" if pct_val >= 0 else ""
                st.metric(
                    label="Current Price", 
                    value=f"{curr}{quote['price']:,.2f}", 
                    delta=f"{sign}{quote['change']:,.2f} ({sign}{pct_val:.2f}%)"
                )
            with anal_col3:
                st.metric(label="Day's Range (Low / High)", value=f"{curr}{quote['low']:,.1f} - {curr}{quote['high']:,.1f}")
            with anal_col4:
                st.metric(label="Day's Volume", value=f"{quote['volume']:,}")
                
            # Chart Period Selector
            period_cols = st.columns([3, 1])
            with period_cols[0]:
                chart_period = st.radio(
                    "Select Chart Timeframe:", 
                    ["1mo", "3mo", "6mo", "1y"], 
                    horizontal=True,
                    index=1,
                    key="chart_period_selector"
                )
            
            # Fetch historic data for plotting
            stock_data = get_stock_data(active_symbol, period=chart_period)
            stock_data = add_indicators(stock_data)
            
            # Plotly Candlestick Chart
            fig = candlestick_chart(stock_data, title=f"{info['name']} ({active_symbol}) - {chart_period} Candlestick Chart")
            st.plotly_chart(fig, use_container_width=True)
            
            # Main detail layout splits
            detail_left_col, detail_right_col = st.columns([1, 1])
            
            with detail_left_col:
                # TECHNICAL INDICATORS CARD
                st.markdown("### 📊 Live Technical Analysis Metrics")
                latest = stock_data.iloc[-1]
                
                rsi_val = latest["RSI"]
                rsi_status = "Oversold (Bullish)" if rsi_val < 30 else "Overbought (Bearish)" if rsi_val > 70 else "Neutral"
                rsi_color = "#00d09c" if rsi_val < 30 else "#ff5050" if rsi_val > 70 else "#ca8a04"
                
                st.markdown(f"""
                <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.01);">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                        <div>
                            <div style="font-size: 12px; color: #64748b; font-weight:600;">RSI (14-period)</div>
                            <div style="font-size: 20px; font-weight:800; color: {rsi_color};">{rsi_val:.2f} <span style="font-size:12px; font-weight:600;">({rsi_status})</span></div>
                        </div>
                        <div>
                            <div style="font-size: 12px; color: #64748b; font-weight:600;">MACD Trend</div>
                            <div style="font-size: 20px; font-weight:800; color: {'#00d09c' if latest['MACD'] > latest['MACD_Signal'] else '#ff5050'};">
                                {'Bullish Crossover' if latest['MACD'] > latest['MACD_Signal'] else 'Bearish Crossover'}
                            </div>
                        </div>
                        <div>
                            <div style="font-size: 12px; color: #64748b; font-weight:600;">SMA (20-day)</div>
                            <div style="font-size: 18px; font-weight:700; color: #1e293b;">{curr}{latest['SMA_20']:,.2f}</div>
                        </div>
                        <div>
                            <div style="font-size: 12px; color: #64748b; font-weight:600;">EMA (20-day)</div>
                            <div style="font-size: 18px; font-weight:700; color: #1e293b;">{curr}{latest['EMA_20']:,.2f}</div>
                        </div>
                        <div style="grid-column: span 2;">
                            <div style="font-size: 12px; color: #64748b; font-weight:600; margin-bottom: 4px;">Bollinger Bands (20, 2)</div>
                            <div style="font-size: 15px; font-weight:700; color: #1e293b; display: flex; justify-content: space-between;">
                                <span>Low: {curr}{latest['BB_Low']:,.2f}</span>
                                <span style="color: #64748b;">Mid: {curr}{latest['BB_Mid']:,.2f}</span>
                                <span>High: {curr}{latest['BB_High']:,.2f}</span>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # FUNDAMENTAL METRICS
                st.markdown("### 🏢 Company Fundamentals")
                mcap = info['market_cap']
                if mcap:
                    if ".NS" in active_symbol or ".BO" in active_symbol:
                        mcap_str = f"₹{mcap/1e7:,.2f} Cr" # Indian style
                    else:
                        mcap_str = f"${mcap/1e9:,.2f} B" # US style
                else:
                    mcap_str = "N/A"
                    
                st.markdown(f"""
                <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.01);">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                        <div>
                            <div style="font-size: 12px; color: #64748b; font-weight:600;">Market Capitalization</div>
                            <div style="font-size: 18px; font-weight:700; color: #1e293b;">{mcap_str}</div>
                        </div>
                        <div>
                            <div style="font-size: 12px; color: #64748b; font-weight:600;">PE Ratio (Trailing)</div>
                            <div style="font-size: 18px; font-weight:700; color: #1e293b;">{f"{info['pe_ratio']:.2f}" if info['pe_ratio'] else 'N/A'}</div>
                        </div>
                        <div>
                            <div style="font-size: 12px; color: #64748b; font-weight:600;">PB Ratio</div>
                            <div style="font-size: 18px; font-weight:700; color: #1e293b;">{f"{info['pb_ratio']:.2f}" if info['pb_ratio'] else 'N/A'}</div>
                        </div>
                        <div>
                            <div style="font-size: 12px; color: #64748b; font-weight:600;">Dividend Yield</div>
                            <div style="font-size: 18px; font-weight:700; color: #1e293b;">{f"{info['dividend_yield']:.2f}%" if info['dividend_yield'] is not None else 'N/A'}</div>
                        </div>
                    </div>
                    <div style="margin-top: 15px; border-top: 1px solid #f1f5f9; padding-top: 15px;">
                        <div style="font-size: 12px; color: #64748b; font-weight:600; margin-bottom: 4px;">Business Description</div>
                        <div style="font-size: 13px; color: #475569; line-height: 1.5; max-height: 120px; overflow-y: auto;">
                            {info['summary']}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            with detail_right_col:
                # AI RECOMMENDATION CARD
                st.markdown("### 🤖 Personal AI Agent Advisor")
                rec_signal = stock_strategy(stock_data)
                
                badge_class = ""
                badge_text = rec_signal
                if "STRONG BUY" in rec_signal:
                    badge_class = "badge-strong-buy"
                elif "BUY" in rec_signal:
                    badge_class = "badge-buy"
                elif "SELL" in rec_signal:
                    badge_class = "badge-sell"
                else:
                    badge_class = "badge-hold"
                    
                st.markdown(f"""
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.02); margin-bottom: 25px;">
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 15px;">
                        <span style="font-weight: 700; color: #1e293b;">Rule-based Advisor Signal</span>
                        <span class="badge {badge_class}">{badge_text}</span>
                    </div>
                    <p style="font-size: 13.5px; color: #475569; line-height: 1.6; margin-bottom: 10px;">
                        Our quantitative script analyzed <b>{active_symbol}</b>'s latest indicators. Here are the core factors driving the <b>{badge_text}</b> signal:
                    </p>
                    <ul style="font-size: 13px; color: #475569; padding-left: 20px; line-height: 1.6;">
                        <li><b>RSI is {latest['RSI']:.1f}</b>: {'Bullish momentum building (under 40)' if latest['RSI'] < 40 else 'Bearish/Overbought signals (over 60)' if latest['RSI'] > 60 else 'Neutral trend strength.'}</li>
                        <li><b>Moving Average crossover</b>: Price is <b>{'above' if latest['Close'] > latest['SMA_20'] else 'below'}</b> the 20-day Simple Moving Average (₹{latest['SMA_20']:,.2f}).</li>
                        <li><b>MACD Status</b>: Trend momentum is <b>{'Bullish (MACD Line is above Signal Line)' if latest['MACD'] > latest['MACD_Signal'] else 'Bearish (MACD Line is below Signal Line)'}</b>.</li>
                        <li><b>Bollinger Band Volatility</b>: Price is situated near the <b>{'lower channel (rebound candidate)' if latest['Close'] < latest['BB_Mid'] else 'upper channel (resistance zone)'}</b>.</li>
                    </ul>
                    <div style="background-color: #f8fafc; border-radius: 8px; padding: 10px; font-size: 12px; color: #64748b; border-left: 3px solid #00d09c; margin-top: 15px;">
                        💡 <b>Agent Recommendation</b>: To get a detailed, LLM-powered advisory response taking market news, fundamentals, and sentiment into account, ask your <b>Chat Agent</b> in the 3rd tab!
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # STOCK NEWS
                st.markdown("### 📰 Recent Market News")
                try:
                    stock_ticker = yf.Ticker(active_symbol)
                    news_list = stock_ticker.news
                    if news_list:
                        for item in news_list[:4]:
                            title = item.get("title", "No Title")
                            pub = item.get("publisher", "Unknown Publisher")
                            link = item.get("link", "#")
                            st.markdown(f"""
                            <div style="padding: 12px; border-bottom: 1px solid #f1f5f9; hover: background-color: #f8fafc;">
                                <div style="font-size: 11px; color: #00d09c; font-weight:700; text-transform:uppercase; margin-bottom: 3px;">{pub}</div>
                                <a href="{link}" target="_blank" style="font-size: 13.5px; font-weight:600; color: #1e293b; text-decoration: none; hover: text-decoration: underline;">
                                    {title}
                                </a>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No recent news found for this stock.")
                except Exception as e:
                    st.write("Could not fetch live news: ", str(e))

                # --- FUTURE TREND & PROFIT/LOSS PREDICTOR ---
                st.markdown("---")
                st.markdown("## 🔮 AI Trend & Future Profit/Loss Predictor")
                st.markdown(f"Mathematical trend extrapolation and AI forward-looking analysis for **{active_symbol}**.")
                
                import numpy as np
                prices = stock_data["Close"].values
                if len(prices) >= 5:
                    days = np.arange(len(prices))
                    m, c = np.polyfit(days, prices, 1)
                    current_price = float(prices[-1])
                    
                    pred_30 = max(0.01, m * (len(prices) + 30) + c)
                    pred_90 = max(0.01, m * (len(prices) + 90) + c)
                    pred_180 = max(0.01, m * (len(prices) + 180) + c)
                    
                    pl_30 = ((pred_30 - current_price) / current_price) * 100
                    pl_90 = ((pred_90 - current_price) / current_price) * 100
                    pl_180 = ((pred_180 - current_price) / current_price) * 100
                    
                    trend_cols = st.columns(3)
                    with trend_cols[0]:
                        pl_color = "return-green" if pl_30 >= 0 else "return-red"
                        sign = "+" if pl_30 >= 0 else ""
                        st.markdown(f"""
                        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.01);">
                            <div style="font-size: 12px; color: #64748b; font-weight: 600; text-transform: uppercase;">30-Day Forecast Target</div>
                            <div style="font-size: 20px; font-weight: 800; color: #0f172a; margin-top: 5px;">{curr}{pred_30:,.2f}</div>
                            <div class="{pl_color}" style="font-size: 13px; margin-top: 4px; font-weight: 700;">
                                {sign}{pl_30:.2f}% {'Expected Profit' if pl_30 >= 0 else 'Expected Loss'}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    with trend_cols[1]:
                        pl_color = "return-green" if pl_90 >= 0 else "return-red"
                        sign = "+" if pl_90 >= 0 else ""
                        st.markdown(f"""
                        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.01);">
                            <div style="font-size: 12px; color: #64748b; font-weight: 600; text-transform: uppercase;">90-Day Forecast Target</div>
                            <div style="font-size: 20px; font-weight: 800; color: #0f172a; margin-top: 5px;">{curr}{pred_90:,.2f}</div>
                            <div class="{pl_color}" style="font-size: 13px; margin-top: 4px; font-weight: 700;">
                                {sign}{pl_90:.2f}% {'Expected Profit' if pl_90 >= 0 else 'Expected Loss'}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    with trend_cols[2]:
                        pl_color = "return-green" if pl_180 >= 0 else "return-red"
                        sign = "+" if pl_180 >= 0 else ""
                        st.markdown(f"""
                        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.01);">
                            <div style="font-size: 12px; color: #64748b; font-weight: 600; text-transform: uppercase;">180-Day Forecast Target</div>
                            <div style="font-size: 20px; font-weight: 800; color: #0f172a; margin-top: 5px;">{curr}{pred_180:,.2f}</div>
                            <div class="{pl_color}" style="font-size: 13px; margin-top: 4px; font-weight: 700;">
                                {sign}{pl_180:.2f}% {'Expected Profit' if pl_180 >= 0 else 'Expected Loss'}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                # Detailed AI Forecast Report Button
                st.write("")
                if "ai_forecasts" not in st.session_state:
                    st.session_state.ai_forecasts = {}
                
                has_report = active_symbol in st.session_state.ai_forecasts
                btn_label = "Update AI Future Forecast Report" if has_report else "Generate AI Future Forecast Report"
                
                f_col1, f_col2, f_col3 = st.columns([1, 2, 1])
                with f_col2:
                    if st.button(btn_label, key="gen_forecast_btn", use_container_width=True):
                        with st.spinner("AI Agent is generating forward-looking analysis report..."):
                            try:
                                forecast_prompt = f"Analyze future prospects, profit/loss risks, growth drivers, and target price stability for the stock {active_symbol}. Suggest whether it is a buy for the future."
                                result = graph.invoke({"messages": [HumanMessage(content=forecast_prompt)]})
                                st.session_state.ai_forecasts[active_symbol] = result["messages"][-1].content
                            except Exception as err:
                                st.error(f"Error generating forecast: {str(err)}")
                                
                if active_symbol in st.session_state.ai_forecasts:
                    st.markdown(f"""
                    <div style="margin-top: 20px; font-weight: 700; font-size: 16px; color: #00d09c;">
                        🔮 AI Agent Future Forecast Report for {active_symbol}:
                    </div>
                    """, unsafe_allow_html=True)
                    st.info(st.session_state.ai_forecasts[active_symbol])
                    
        except Exception as e:
            st.error(f"Could not load data for symbol '{active_symbol}'. Make sure it is a valid ticker.")
            st.info("Ensure Indian tickers end with '.NS' or '.BO' (e.g. RELIANCE.NS, OLAELEC.NS, CUPID.NS). Try selecting one of the popular stocks above.")

# ==============================================================================
# TAB 2: PORTFOLIO TRACKER
# ==============================================================================
with tab_portfolio:
    st.subheader("Simulated Investment Tracker")
    st.markdown("Monitor your personal stock holdings and track real-time valuations, total returns, and 1-day gains.")
    
    # CALCULATE LIVE VALUATIONS
    total_invested = 0.0
    total_current_value = 0.0
    total_1d_returns = 0.0
    
    holdings_with_prices = []
    
    # Process portfolio calculations
    for h in st.session_state.holdings:
        sym = h["symbol"]
        qty = h["quantity"]
        buy_p = h["buy_price"]
        invested = qty * buy_p
        total_invested += invested
        
        try:
            quote = get_live_quote(sym)
            live_p = quote["price"]
            daily_change = quote["change"]
            
            curr_val = qty * live_p
            total_current_value += curr_val
            
            one_day_ret = qty * daily_change
            total_1d_returns += one_day_ret
            
            tot_ret = curr_val - invested
            tot_ret_pct = (tot_ret / invested) * 100
            
            holdings_with_prices.append({
                "symbol": sym,
                "quantity": qty,
                "buy_price": buy_p,
                "live_price": live_p,
                "invested": invested,
                "current_val": curr_val,
                "total_return": tot_ret,
                "total_return_pct": tot_ret_pct,
                "one_day_return": one_day_ret,
                "one_day_return_pct": quote["pct_change"]
            })
        except Exception:
            # Fallback if price loading failed
            total_current_value += invested
            holdings_with_prices.append({
                "symbol": sym,
                "quantity": qty,
                "buy_price": buy_p,
                "live_price": buy_p,
                "invested": invested,
                "current_val": invested,
                "total_return": 0.0,
                "total_return_pct": 0.0,
                "one_day_return": 0.0,
                "one_day_return_pct": 0.0
            })

    # PORTFOLIO SUMMARY CARDS
    tot_return_val = total_current_value - total_invested
    tot_return_pct = (tot_return_val / total_invested * 100) if total_invested > 0 else 0.0
    
    sum_col1, sum_col2, sum_col3, sum_col4 = st.columns(4)
    with sum_col1:
        st.markdown(f"""
        <div class="portfolio-metric-card">
            <div class="portfolio-metric-title">Total Invested</div>
            <div class="portfolio-metric-value">₹{total_invested:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with sum_col2:
        st.markdown(f"""
        <div class="portfolio-metric-card">
            <div class="portfolio-metric-title">Current Value</div>
            <div class="portfolio-metric-value">₹{total_current_value:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with sum_col3:
        ret_color = "return-green" if tot_return_val >= 0 else "return-red"
        sign = "+" if tot_return_val >= 0 else ""
        st.markdown(f"""
        <div class="portfolio-metric-card">
            <div class="portfolio-metric-title">Total Returns</div>
            <div class="portfolio-metric-value {ret_color}">{sign}₹{tot_return_val:,.2f}</div>
            <div class="{ret_color}" style="font-size:12px; margin-top:2px; font-weight:600;">{sign}{tot_return_val:,.2f} ({tot_return_pct:+.2f}%)</div>
        </div>
        """, unsafe_allow_html=True)
    with sum_col4:
        d_color = "return-green" if total_1d_returns >= 0 else "return-red"
        sign_1d = "+" if total_1d_returns >= 0 else ""
        pct_1d = (total_1d_returns / total_invested * 100) if total_invested > 0 else 0.0
        st.markdown(f"""
        <div class="portfolio-metric-card">
            <div class="portfolio-metric-title">1D Returns</div>
            <div class="portfolio-metric-value {d_color}">{sign_1d}₹{total_1d_returns:,.2f}</div>
            <div class="{d_color}" style="font-size:12px; margin-top:2px; font-weight:600;">{sign_1d}{pct_1d:+.2f}%</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.write("---")
    
    # DOCK ADDITION AND DISPLAY LIST
    port_list_col, port_add_col = st.columns([2, 1])
    
    with port_list_col:
        st.subheader("Your Holdings")
        if not holdings_with_prices:
            st.info("Your portfolio is currently empty. Add stocks using the right-hand panel!")
        else:
            # HTML Table representation for beautiful Groww layout
            table_html = """
            <table style="width:100%; border-collapse: collapse; text-align: left; font-size: 14px;">
                <thead>
                    <tr style="border-bottom: 2px solid #f1f5f9; color: #64748b; font-weight: 600;">
                        <th style="padding:12px 8px;">Symbol</th>
                        <th style="padding:12px 8px;">Qty</th>
                        <th style="padding:12px 8px;">Avg Buy Price</th>
                        <th style="padding:12px 8px;">Live Price</th>
                        <th style="padding:12px 8px;">Invested</th>
                        <th style="padding:12px 8px;">Current Value</th>
                        <th style="padding:12px 8px; text-align:right;">Total Return</th>
                    </tr>
                </thead>
                <tbody>
            """
            for h in holdings_with_prices:
                ret_color = "return-green" if h["total_return"] >= 0 else "return-red"
                sign = "+" if h["total_return"] >= 0 else ""
                table_html += f"""
                    <tr style="border-bottom: 1px solid #f1f5f9;" class="table-row">
                        <td style="padding:16px 8px; font-weight: 700; color: #00d09c;">{h['symbol']}</td>
                        <td style="padding:16px 8px; font-weight: 500;">{h['quantity']}</td>
                        <td style="padding:16px 8px;">₹{h['buy_price']:,.2f}</td>
                        <td style="padding:16px 8px; font-weight: 600;">₹{h['live_price']:,.2f}</td>
                        <td style="padding:16px 8px;">₹{h['invested']:,.2f}</td>
                        <td style="padding:16px 8px; font-weight: 600;">₹{h['current_val']:,.2f}</td>
                        <td style="padding:16px 8px; text-align:right;" class="{ret_color}">
                            {sign}₹{h['total_return']:,.2f}<br>
                            <span style="font-size:11px;">{sign}{h['total_return_pct']:.2f}%</span>
                        </td>
                    </tr>
                """
            table_html += "</tbody></table>"
            st.markdown(table_html, unsafe_allow_html=True)
            
            # Adding delete selectors below the table for simple row removing
            st.write("")
            del_cols = st.columns([3, 1])
            with del_cols[0]:
                to_delete = st.selectbox(
                    "Select holding to remove:", 
                    options=[h["symbol"] for h in st.session_state.holdings],
                    key="remove_selector"
                )
            with del_cols[1]:
                st.write(" ")
                st.write(" ")
                if st.button("Delete Holding", use_container_width=True):
                    st.session_state.holdings = [h for h in st.session_state.holdings if h["symbol"] != to_delete]
                    st.success(f"Removed {to_delete} from portfolio.")
                    st.rerun()
                    
    with port_add_col:
        st.subheader("Add Stock to Portfolio")
        with st.form("add_holding_form", clear_on_submit=True):
            add_sym = st.text_input("Stock Symbol (e.g. RELIANCE.NS, OLAELEC.NS, AAPL)", placeholder="RELIANCE.NS").strip().upper()
            add_qty = st.number_input("Quantity", min_value=1, value=10, step=1)
            add_price = st.number_input("Purchase Price (₹ or $)", min_value=0.01, value=100.0, step=1.0)
            
            submit = st.form_submit_button("Add to Portfolio", use_container_width=True)
            if submit:
                if not add_sym:
                    st.error("Please enter a valid stock symbol.")
                else:
                    # Append new holding
                    st.session_state.holdings.append({
                        "symbol": add_sym,
                        "quantity": add_qty,
                        "buy_price": add_price
                    })
                    st.success(f"Added {add_qty} shares of {add_sym} to portfolio!")
                    st.rerun()

# ==============================================================================
# TAB 3: PERSONAL AI AGENT CHAT
# ==============================================================================
with tab_ai_agent:
    st.subheader("Interact with your Personal AI Stock Agent")
    st.markdown("""
    Ask questions about any stock, check live rates, technical metrics, latest news, and get precise Buy/Sell advisory.
    Our agent is equipped with LangGraph tools and Groq llama-3 intelligence.
    """)
    
    # Pre-baked suggestions column
    st.write("💡 **Quick Questions Suggestions:**")
    sug_cols = st.columns(4)
    sug_prompts = [
        "Reliance.ns buy karu ya sell?",
        "Show fundamental analysis for TCS.ns",
        "Olactric (OLAELEC.ns) stock technical report",
        "Get recent market news of TATAMOTORS.ns"
    ]
    for i, p in enumerate(sug_prompts):
        with sug_cols[i]:
            if st.button(p, key=f"sug_btn_{i}", use_container_width=True):
                # Append to chat
                st.session_state.chat_history.append(HumanMessage(content=p))
                with st.spinner("Agent is analyzing the query..."):
                    try:
                        result = graph.invoke({"messages": st.session_state.chat_history})
                        st.session_state.chat_history = result["messages"]
                    except Exception as err:
                        st.error(f"Error: {str(err)}")
                st.rerun()
                
    st.write("---")
    
    # CHAT HISTORY VIEW
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history:
            if isinstance(msg, HumanMessage):
                st.markdown(f'<div class="chat-bubble-user">🙋‍♂️ <b>You:</b><br>{msg.content}</div>', unsafe_allow_html=True)
            elif isinstance(msg, AIMessage) and msg.content:
                st.markdown(f'<div class="chat-bubble-agent">🤖 <b>Agent:</b><br>{msg.content}</div>', unsafe_allow_html=True)
                
    # CHAT INPUT
    user_query = st.chat_input("Type your message here (e.g. 'TATA MOTORS buy karu ya sell?')...")
    if user_query:
        # Append User Message
        st.session_state.chat_history.append(HumanMessage(content=user_query))
        
        # Reload to render user bubble instantly
        st.rerun()

# Execute background processing of the user input if it was just added
if len(st.session_state.chat_history) > 0 and isinstance(st.session_state.chat_history[-1], HumanMessage):
    with tab_ai_agent:
        with st.spinner("Thinking..."):
            try:
                result = graph.invoke({"messages": st.session_state.chat_history})
                st.session_state.chat_history = result["messages"]
                st.rerun()
            except Exception as e:
                st.error(f"Agent experienced an issue processing your query: {str(e)}")
                st.info("Check if your Groq API key is valid in stock_ai_agent/.env.")