import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from si_prefix import si_format

st.set_page_config(layout="wide")
st.title("Stock Price Viewer with Custom Date Range")
st.divider()

sp500_url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
tables = pd.read_html(sp500_url)
sp500_table = tables[0]
tickers = sp500_table['Symbol'].tolist()
col1,col2,col3=st.columns(3)
ticker = col1.selectbox("Select Stock Ticker", options=tickers)
st.divider()
@st.cache_data
def get_data(ticker):
    ticker = yf.Ticker(ticker)
    data = ticker.history(period="max")
    return data

if ticker:
    data = get_data(ticker)
    data.index=pd.to_datetime(data.index).tz_localize(None)
    earliest_date = data.index.min()
    latest_date = data.index.max()

    start_date = col2.date_input(
        "Start Date",
        value=earliest_date,
        min_value=earliest_date,
        max_value=latest_date
    )

    end_date = col3.date_input(
        "End Date",
        value=latest_date,
        min_value=earliest_date,
        max_value=latest_date
    )

    if end_date < start_date:
        st.error("End date must be after the start date.")
    elif (end_date - start_date).days < 10:
        st.error("The date range must be at least 10 days.")
    else:
        #different data to track
        tab_names=["Sales","Open","Close","High","Low","Volume"]
        tabs = st.tabs(tab_names)

        #prepairing data
        filtered_data = data.loc[start_date:end_date]
        filtered_data["Sales"]=((filtered_data["High"]+filtered_data["Low"])/2)*filtered_data["Volume"]
        dividends=filtered_data[filtered_data["Dividends"]!=0]
        split=filtered_data[filtered_data["Stock Splits"]!=0]

        for i,tab in enumerate(tab_names):
            with tabs[i]:
                last = filtered_data[tab].iloc[-1]
                mean = filtered_data[tab].mean()
                first = filtered_data[tab].iloc[0]
                best = filtered_data[tab].max()
                worst = filtered_data[tab].min()

                with st.container(border=True):
                    st.subheader("comparing values to mean")

                    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
                    if tab == "Volume":
                        col1.metric(f"First value", f"{si_format(first,precision=2).replace(" ","").replace("G","B")}",f"{((first - mean) / mean) * 100:.2f}%")
                        col5.metric(f"Last value", f"{si_format(last,precision=2).replace(" ","").replace("G","B")}",f"{((last - mean) / mean) * 100:.2f}%")
                        col3.metric(f"Mean value", f"{si_format(mean, precision=2).replace(" ","").replace("G", "B")}")
                        col2.metric(f"Best value", f"{si_format(best, precision=2).replace(" ","").replace("G","B")}",f"{((best - mean) / mean) * 100:.2f}%")
                        col4.metric(f"Worst value", f"{si_format(worst, precision=2).replace(" ","").replace("G","B")}",f"{((worst - mean) / mean) * 100:.2f}%")
                    else:
                        col1.metric(f"First value", f"${si_format(float(first),precision=2).replace(" ","").replace("G","B")}",f"{((first - mean) / mean) * 100:.2f}%")
                        col5.metric(f"Last value", f"${si_format(float(last),precision=2).replace(" ","").replace("G","B")}",f"{((last - mean) / mean) * 100:.2f}%")
                        col3.metric(f"Mean value", f"${si_format(mean, precision=2).replace(" ","").replace("G", "B")}")
                        col2.metric(f"Best value", f"${si_format(float(best), precision=2).replace(" ","").replace("G","B")}",f"{((best - mean) / mean) * 100:.2f}%")
                        col4.metric(f"Worst value", f"${si_format(float(worst), precision=2).replace(" ","").replace("G","B")}",f"{((worst - mean) / mean) * 100:.2f}%")

                st.divider()

                st.header(f"{ticker} Price History for {tab} values between: {start_date.strftime("%B %d, %Y")} and {end_date.strftime("%B %d, %Y")}",divider='gray')

                fig=go.Figure()

                fig.add_trace(go.Scatter(x=filtered_data.index,y=filtered_data[tab],mode="lines+markers",marker=dict(size=2,color="rgba(255,255,255,0.9)"),line=dict(color="#1f77b4"),name=f"{tab} data"))

                fig.update_layout(
                    yaxis=dict(
                        fixedrange=True,
                        title="Trade count" if tab=="Volume" else "Estimated total sales" if tab=="Sales" else "Stock price",
                        tickprefix="$" if tab!="Volume" else "",
                    ),
                    xaxis=dict(
                        title="Date",
                    ),
                    modebar=dict(
                        remove=['pan', 'select2d', 'lasso2d', 'zoomIn', 'zoomOut']
                    ),
                    margin=dict(l=0, r=0, b=0, t=0, pad=0),
                )
                fig.update_traces(
                    hovertemplate="%{x|%B %d, %Y}<br>%{text}<extra></extra>",
                    text=[(f'Stock split of {si_format(float(ss), precision=2).replace(" ","").replace("G","B")}<br>' if ss!=0 else "")+f'{si_format(float(v), precision=2).replace(" ","").replace("G","B")} Units of {ticker} traded'+(f'<br>Dividend: ${si_format(float(d), precision=2).replace(" ","").replace("G","B")}' if d!=0 else "")+f'<br>${si_format(float(s), precision=2).replace(" ","").replace("G","B")} estimated total sales'+f'<br>Open price: ${si_format(float(o), precision=2).replace(" ","").replace("G","B")}'+f'<br>Close price: ${si_format(float(c), precision=2).replace(" ","").replace("G","B")}'+f'<br>Highest price: ${si_format(float(h), precision=2).replace(" ","").replace("G","B")}'+f'<br>Lowest price: {si_format(float(l), precision=2).replace(" ","").replace("G","B")}' for v, s, o, c, h, l, d, ss in filtered_data[['Volume','Sales', 'Open', 'Close', 'High', 'Low', "Dividends", "Stock Splits"]].values])

                st.plotly_chart(fig,use_container_width=True)