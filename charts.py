import yfinance as yf
import plotly.graph_objects as go

def candlestick_chart(data, title="Stock Candlestick Chart"):

    fig = go.Figure(
        data=[
            go.Candlestick(
                x=data.index,
                open=data["Open"],
                high=data["High"],
                low=data["Low"],
                close=data["Close"],
                increasing_line_color='#00d09c', # Groww Green
                decreasing_line_color='#ff5050'  # Groww Red
            )
        ]
    )

    fig.update_layout(
        title=title,
        template="plotly_white",
        xaxis_rangeslider_visible=False,
        margin=dict(l=40, r=40, t=40, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            showgrid=True,
            gridcolor="#f0f0f0",
            title="Date"
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#f0f0f0",
            title="Price"
        )
    )

    return fig