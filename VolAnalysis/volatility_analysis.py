import numpy as np
import streamlit as st
from utils.utils import calculate_stock_volatility, securities, fetch_current_price, fetch_dividend_yield, fetch_interest_rate, continuous_rate, extract_security_name
from VolAnalysis.data_analysis import fetch_option_data, calculate_implied_volatility
import plotly.express as px
import plotly.graph_objects as go
from scipy.interpolate import griddata


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

    # interest_rate = st.number_input(
    #   label = "Risk free rate",
    #   value = continuous_rate(fetch_interest_rate()),
    #   key = "risk_free_rate"
    # )

    # dividend_yield = st.number_input(
    #   label = "Dividend yield",
    #   value = continuous_rate(fetch_dividend_yield(st.session_state.stock_ticker)),
    #   key = "dividend_yield"
    # )

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

    IV = option_data["impliedVolatility"]
    strike = option_data["strike"]
    ttm = option_data["ttm"]

    # interp = interp2d(x=strike, y=ttm, z=IV, kind="cubic")
    # strike_interp = np.linspace(strike.min(), strike.max() + 1, 100)
    # ttm_interp = np.linspace(ttm.min(), ttm.max() + 1, 100)
    # iv_interp = interp(strike_interp, ttm_interp)
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
        zaxis_title='Volatility'
    ),
    title='Surface Plot of Volatility Skew'
  )


  st.plotly_chart(fig)

  option_data.sort_values(by="strike")
  fig = px.scatter(
    option_data, 
    x = "strike",
    y = "impliedVolatility",
    title = f"Implied Volatility Over Strike for {st.session_state.stock_ticker}"
  )

  fig.update_layout(
    xaxis_title = "Strike",
    yaxis_title = "Implied Volatility",
  )
  st.plotly_chart(fig)






