import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# Fetch S&P 500 companies (just a sample of popular stocks)
def get_sp500_tickers():
    sp500_url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    tables = pd.read_html(sp500_url)  # Reads all tables from the Wikipedia page
    sp500_table = tables[0]  # The first table contains the stock tickers
    tickers = sp500_table['Symbol'].tolist()  # Extracting the tickers as a list
    return tickers

# Fetch the list of S&P 500 tickers
sp500_tickers = get_sp500_tickers()
ticker=sp500_tickers[0]
ticker = yf.Ticker(ticker)
data=ticker.history(period="1mo")
print("making fig")
fig=go.Figure()
fig.add_trace(go.Scatter(x=data.index,y=data["Close"],mode="lines",name="test"))
print("done making fig")
fig.show()