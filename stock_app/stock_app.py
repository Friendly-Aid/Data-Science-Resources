import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd

st.title("Stock Price Viewer with Custom Date Range")

sp500_url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
tables = pd.read_html(sp500_url)
sp500_table = tables[0]
tickers = sp500_table['Symbol'].tolist()
ticker = st.selectbox("Select Stock Ticker", options=tickers)

@st.cache_data
def get_stock_data(ticker):
    stock_data = yf.download(ticker)
    return stock_data

if ticker:
    stock_data = get_stock_data(ticker)

    earliest_date = stock_data.index.min().date()
    latest_date = stock_data.index.max().date()

    col1,col2=st.columns(2)
    start_date = col1.date_input(
        "Start Date",
        value=earliest_date,
        min_value=earliest_date,
        max_value=latest_date
    )

    end_date = col2.date_input(
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
        filtered_data = stock_data.loc[start_date:end_date]
        rolling_mean = filtered_data['Close'].rolling(window=10).mean()

        last_close = filtered_data['Close'].iloc[-1]
        mean_close = filtered_data['Close'].mean()
        percent_above_mean = ((last_close - mean_close) / mean_close) * 100

        first_close = filtered_data['Close'].iloc[0]
        percent_since_start = ((last_close - first_close) / first_close) * 100

        col1.metric("Last Value Percent Above Mean", f"{float(last_close):.2f}", f"{float(percent_above_mean):.2f}%")
        col2.metric("Last Value Percent Since Start", f"{float(last_close):.2f}", f"{float(percent_since_start):.2f}%")

        plt.figure(figsize=(10, 6))
        plt.plot(filtered_data.index, filtered_data['Close'], label="Close Price")
        plt.plot(filtered_data.index, rolling_mean, label="Rolled Close Price", color='#0ac80abf', linestyle='-')
        plt.title(f"{ticker} Stock Price from {start_date} to {end_date}")
        plt.xlabel("Date")
        plt.ylabel("Price (USD)")
        plt.grid(True)
        plt.legend()

        st.pyplot(plt)
