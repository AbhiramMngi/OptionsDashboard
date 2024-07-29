import pandas as pd
import numpy as np
import yfinance as yf
import streamlit as st
from utils.utils import calculate_stock_volatility, securities, fetch_current_price, fetch_dividend_yield, fetch_interest_rate, continuous_rate, extract_security_name
from VolAnalysis.data_analysis import fetch_option_data
import plotly.express as px
import plotly.graph_objects as go
from scipy.interpolate import griddata


def calculate_historical_volatility(sec, days):
  # days = 252 * 5
  sec = extract_security_name(sec)
  data = yf.download([sec], period="1y", interval="1d")
  vol = pd.DataFrame()
  data["logReturns"] = np.log(data['Close'] / data['Close'].shift(1)).dropna()

  return data["logReturns"].pct_change().std() * np.sqrt(252)

def render_volatility_dashboard():
  with st.form("vol_form"):
    stock_tickers = st.selectbox(
      label = "Select Stock Ticker",
      options = securities,
      index = 39,
      key = "stock_ticker"
    )

    spot_price = st.number_input(
      label = "Spot Price",
      min_value = 0.0,
      value = fetch_current_price(st.session_state.stock_ticker),
      key = "spot_price",
      disabled=True
    )

    days = st.number_input(
      label = "Number of Days",
      min_value = 1,
      max_value = 365,
      value = 30,
      key = "days"
    )
    submit = st.form_submit_button(
      "Get Volatility Analysis",
      type="primary"
    )
  if submit or st.session_state.flag:
    st.session_state.flag = False
    data = calculate_stock_volatility(
      sec=st.session_state.stock_ticker,
      days = st.session_state.days
    )

    fig = px.line(
      data, 
      x = "date",
      y = "vol",
      title = f"Volatility of {st.session_state.stock_ticker} in a window of {st.session_state.days} days"
    )

    fig.update_layout(
      xaxis_title = "Date",
      yaxis_title = "Volatility",
    )

    st.plotly_chart(fig)

    option_data = fetch_option_data(
      st.session_state.stock_ticker,
      spot_price = st.session_state.spot_price
    )

    # implied_volatility = calculate_implied_volatility(option_data)
    option_data["impliedVolatility"] = option_data["impliedVolatility"]/100

    strike_range = np.linspace(option_data['strike'].min(), option_data['strike'].max(), 100)
    ttm_range = np.linspace(option_data['ttm'].min(), option_data['ttm'].max(), 100)
    strike_grid, ttm_grid = np.meshgrid(strike_range, ttm_range)

    vol_grid = griddata(
      (option_data["strike"], option_data["ttm"]),
      option_data["impliedVolatility"],
      (strike_grid, ttm_grid),
      method="cubic"
    )

    fig = go.Figure(data=[go.Surface(
    x=strike_grid,
    y=ttm_grid,
    z=vol_grid,
    colorscale='Viridis'
  )])
    
  fig.update_layout(
    scene=dict(
        xaxis_title='Strike',
        yaxis_title='Time to Maturity',
        zaxis_title='Volatility',
        zaxis=dict(range=[0, 0.2])
    ),
    title='Surface Plot of Volatility Skew'
  )


  st.plotly_chart(fig)

  od = option_data[["strike", "impliedVolatility"]].groupby("strike").mean()
  od.reset_index(inplace=True)
  fig = px.scatter(
    od, 
    x = "strike",
    y = "impliedVolatility",
    title = f"Implied Volatility Over Strike for {st.session_state.stock_ticker}",

  )


  fig.update_layout(
    xaxis_title = "Strike",
    yaxis_title = "Implied Volatility",
    # yaxis=dict(range=[0, 0.024])
  )
  st.plotly_chart(fig)

  st.success(f"The following plots show the volatility skew with respect to Time to maturity and Strike price of the options available in the market, the calculated historical volatility is {calculate_historical_volatility(st.session_state.stock_ticker, st.session_state.days):.3f}")






