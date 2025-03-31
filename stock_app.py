import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import datetime

# Streamlit title
st.title("Stock Price Viewer with Custom Date Range")

# User input for selecting a stock ticker
sp500_url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
tables = pd.read_html(sp500_url)  # Reads all tables from the Wikipedia page
sp500_table = tables[0]  # The first table contains the stock tickers
tickers = sp500_table['Symbol'].tolist()
ticker = st.selectbox("Select Stock Ticker", options=tickers)

# Function to get stock data and find the earliest and latest dates
@st.cache_data
def get_stock_data(ticker):
    # Download stock data from Yahoo Finance
    stock_data = yf.download(ticker)
    return stock_data

# Fetch stock data if ticker is selected
if ticker:
    stock_data = get_stock_data(ticker)

    # Get the earliest and latest available dates in the stock data
    earliest_date = stock_data.index.min().date()
    latest_date = stock_data.index.max().date()
    # Date input widgets with dynamic behavior based on stock selection
    col1,col2=st.columns(2)
    start_date = col1.date_input(
        "Start Date",
        value=earliest_date,  # Default to the earliest date
        min_value=earliest_date,  # Set the minimum date
        max_value=latest_date  # Set the maximum date
    )

    end_date = col2.date_input(
        "End Date",
        value=latest_date,  # Default to the latest date
        min_value=earliest_date,  # Set the minimum date
        max_value=latest_date  # Set the maximum date
    )

    # Ensure the distance between the start and end dates is at least 10 days
    if end_date < start_date:
        st.error("End date must be after the start date.")
    elif (end_date - start_date).days < 10:
        st.error("The date range must be at least 10 days.")
    else:
        # Filter the data based on the selected date range
        filtered_data = stock_data.loc[start_date:end_date]
        rolling_mean = filtered_data['Close'].rolling(window=10).mean()
        # Plot the closing price
        last_close = filtered_data['Close'].iloc[-1]
        mean_close = filtered_data['Close'].mean()
        percent_above_mean = ((last_close - mean_close) / mean_close) * 100

        # Calculate Percent Since the Beginning
        first_close = filtered_data['Close'].iloc[0]
        percent_since_start = ((last_close - first_close) / first_close) * 100

        # Display percentages using Streamlit's st.metric()
        col1.metric("Percent Above Mean", f"{float(last_close):.2f}", f"{float(percent_above_mean):.2f}%")
        col2.metric("Percent Since Start", f"{float(last_close):.2f}", f"{float(percent_since_start):.2f}%")

        plt.figure(figsize=(10, 6))
        plt.plot(filtered_data.index, filtered_data['Close'], label="Close Price")
        plt.plot(filtered_data.index, rolling_mean, label="Rolled Close Price", color='#0ac80abf', linestyle='-')
        plt.title(f"{ticker} Stock Price from {start_date} to {end_date}")
        plt.xlabel("Date")
        plt.ylabel("Price (USD)")
        plt.grid(True)
        plt.legend()

        # Display plot in Streamlit
        st.pyplot(plt)
