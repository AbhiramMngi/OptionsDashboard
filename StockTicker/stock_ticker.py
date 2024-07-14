import yfinance as yf 
import pandas as pd
import streamlit as st
import plotly.express as px

TIME_FRAMES_PERIOD = {
  "Past Day": "1d",
  "Past Month": "1mo",
  "Past Year": "1y"
}
TIME_FRAMES_INTERVAL = {
  "Past Day": "1m",
  "Past Month": "1h",
  "Past Year": "1d"
}

FLAG = True

def render_stock_data():

  ticker_list = ["AAPL", "GOOGL"]
  period = "1y"
  interval = "1d"
  time_interval = "Date"
  data = yf.download(tickers=ticker_list, period=period, interval=interval)
  data.reset_index(inplace=True)

  with st.sidebar:
    with st.form("stock_names"):
      tickers = st.text_input(
        label = "Stock Tickers",
        value = "",
        placeholder="AAPL GOOGL",
      )

      time_frame = st.selectbox(
        "Select Time Frame",
        ("Past Day", "Past Month", "Past Year"),
        index=None,
        placeholder="Select Period"
      )

      submit = st.form_submit_button(
        label="Get Ticker Data",
        type="primary"
      )

  if submit:
    # print(time_frame)
    data, period, interval, ticker_list, time_interval = fetch_data(tickers, time_frame)

  
  
  plot_data(data, period, ticker_list)

  if "Date" in data.columns: 
    data["Date"] = data["Date"].dt.date
    
  st.dataframe(
    data[[time_interval, *[f"Price_{i}" for i in ticker_list]]],
    use_container_width=True
  )

class StockTicker:
  def __init__(self, ticker_list, period="1y", interval="1d"):
    self.tickers = ticker_list
    self.period = period
    self.interval = interval
  

  def fetch_stock_data(self):

    data = yf.download(tickers=self.tickers, period=self.period, interval=self.interval)
    data.reset_index(inplace=True)

    data = process_columns(data, self.tickers, self.period)
    return data
  
  

def process_columns(data, tickers, period):

  time_interval = "Datetime" if period != "1y" else "Date"

  if isinstance(data.columns, pd.MultiIndex): 
    data.columns = ['_'.join(col).strip() if col[0] not in ["Date", "Datetime"] else col[0] for col in data.columns]
  else:
    data.columns = [f"{ticker}_{tickers[0]}" if ticker not in ["Date", "Datetime"] else ticker for ticker in data.columns]
  
  for i in tickers:
    data[f"Price_{i}"] = (data[f"Low_{i}"] + data[f"High_{i}"])/2
  print("Ao", [time_interval, *[f"Price_{i}" for i in tickers]], data.columns)
  # data = data[[time_frame, *[f"Price_{i}" for i in tickers]]]

  return data

def fetch_data(tickers, time_frame):

  ticker_list = tickers.split() if len(tickers) > 0 else ["AAPL", "GOOGL"]
  period, interval = (TIME_FRAMES_PERIOD.get(time_frame, "1y")), TIME_FRAMES_INTERVAL.get(time_frame,"1d")
  
  stock_ticker = StockTicker(ticker_list, period, interval)
  time_interval = "Datetime" if period != "1y" else "Date"
  data = stock_ticker.fetch_stock_data()

  return data, period, interval, ticker_list, time_interval
  
def plot_data(data, period, ticker_list):
  global FLAG
  if FLAG: 
    data = process_columns(data, ticker_list, period)
    FLAG = False
  time_frame = "Datetime" if period != "1y" else "Date"
  fig = px.line(
    data,
    x = time_frame,
    y = [f"Price_{i}" for i in ticker_list],
    title = "Stock Prices"
  )

  fig.update_layout(
    xaxis_title = time_frame,
    yaxis_title = "Stock Price",
    legend_title = "Stocks"
  )
  event = st.plotly_chart(fig, use_container_width= True)
  event