import numpy as np 
import pandas as pd 
import yfinance as yf
import streamlit as st
import re
from datetime import date
from bs4 import BeautifulSoup
import requests
from OptionPricer.black_scholes import BlackScholesPricer
from OptionPricer.utils.utils import PricerInput
import plotly.express as px

securities = [i[0] for i in pd.read_csv('securities.csv').values.tolist()]

def extract_security_name(sec):
  return re.match(r'^(.*) \((.*)\)$', sec).group(2)

def get_window_size(expiry):
  days = (expiry - date.today()).days
  if days <= 10: return 10
  if days <= 20: return 20
  if days <= 30: return 30
  if days <= 60: return 60
  if days <= 90: return 90
  if days <= 120: return 120
  if days <= 150: return 150
  return 180

def scrape_stock_volatility(sec):
  sec = extract_security_name(sec)
  window_size = get_window_size(st.session_state.expiration_date)
  url = f'https://www.alphaquery.com/stock/{sec}/volatility-option-statistics/{window_size}-day/parkinson-historical-volatility' 
  response = requests.get(url)

  soup = BeautifulSoup(response.content, 'html.parser')

  selector = '#indicator-parkinson-historical-volatility .indicator-figure-inner'  # Example: 'p' for paragraph tags

  elements = soup.select(selector)
  return np.float32(elements[0].get_text()[:-1])


def format_period(days):
  if days < 30:
    return "1mo"
  if days <= 180:
    return "6mo"
  else:
    return "1y"


def fetch_interest_rate():
  treasury_ticker = "^TNX"

  treasury = yf.Ticker(treasury_ticker)
  treasury_data = treasury.history(period="1mo")
  risk_free_rate = treasury_data['Close'].iloc[-1] / 100
  
  return risk_free_rate

def fetch_current_price(sec):
  if sec is None:
    sec = "Apple Inc. (AAPL)"
  sec = extract_security_name(sec)
  data = yf.Ticker(sec)
  return data.info['previousClose']

def fetch_dividend_yield(sec):
  if sec is None:
    sec = "Apple Inc. (AAPL)"
  sec = extract_security_name(sec)
  data = yf.Ticker(sec)
  return data.info.get('dividendYield', 0.0)

def render_option_dashboard():

  with st.sidebar:
    option_style = st.selectbox(
      "Select Option Style",
      ("European", "American"),
      key = "option_style",
      index=0,
      placeholder="Select Option Style"
    )

  cols = st.columns(2)
  with cols[0]:
    stock_name = st.selectbox(
      "Select Stock Name",
      options = securities,
      key = "stock_name",
      index = 39,
    )
  with cols[1]:
    expiration_date = st.date_input("Select Expiration Date", key="expiration_date", min_value=pd.Timestamp.now())

  with st.form("option_pricer"):
    cols = st.columns(2)
    with cols[0]:
      spot_price = st.number_input(
        "Spot Price ($USD)",
        placeholder = "Enter Spot Price",
        value = fetch_current_price(st.session_state.stock_name),
        disabled = True
      )
    with cols[1]:
      strike_price = st.number_input(
        "Strike Price ($USD)",
        min_value = 0.0,
        max_value = 10000.0,
        step = 10.0,
        value = spot_price,
        key = "strike_price" 
      )
    
    dividend_yield = st.number_input(
      "Dividend Yield (%)",
      min_value = 0.0,
      max_value = 100.0,
      step = 1.0,
      value = fetch_dividend_yield(st.session_state.stock_name) * 100,
      key = "dividend_yield"
    )

    risk_free_rate = st.number_input(
      "Risk-Free Rate (%) (10-year American Treasury Bond)",
      min_value = 0.0,
      max_value = 100.0,
      step = 0.1,
      value = fetch_interest_rate() * 100,
      key = "risk_free_rate",
    )

    volatility = st.number_input(
      "Volatility (%)",
      min_value = 0.0,
      max_value = 100.0,
      step = 0.01,
      value = scrape_stock_volatility(st.session_state.stock_name) * 100,
      key = "volatility",
    )

    submit = st.form_submit_button(
      "Calculate Option Price",
      type = "primary"
    )
    
  if submit:
    if st.session_state.option_style == "European":
      pricer = BlackScholesPricer()
    
    pricer_input = PricerInput(
      stock_ticker=stock_name,
      spot_price=spot_price,
      strike_price=strike_price,
      risk_free_rate=risk_free_rate,
      volatility=volatility,
      expiration_date=expiration_date,
      dividend_rate=dividend_yield
    )

    summary = pricer.summary(pricer_input)
    with st.sidebar:

      st.success(f"Call Price: {summary.call_price[13]:.2f}")
      st.error(f"Put Price: {summary.put_price[13]:.2f}")
      
      cols = st.columns(2)
      with cols[0]:
        
        st.metric("Call Delta",f"{summary.greeks.delta_call[13]:.2f}")
      with cols[1]:
        st.metric("Put Delta:", f"{summary.greeks.delta_put[13]:.2f}")
      st.metric("Gamma", f"{summary.greeks.gamma[13]:.2f}")
      st.metric("Vega", f"{summary.greeks.vega[13]:.2f}")
      theta_cols = st.columns(2)
      with theta_cols[0]:
        st.metric("Call Theta", f"{summary.greeks.theta_call[13]:.2f}")
      with theta_cols[1]:
        st.metric("Put Theta:", f"{summary.greeks.theta_put[13]:.2f}")

      rho_cols = st.columns(2)
      with rho_cols[0]:
        st.metric("Call Rho", f"{summary.greeks.rho_call[13]:.2f}")
      with rho_cols[1]:
        st.metric("Put Rho:", f"{summary.greeks.rho_put[13]:.2f}")

    df = pd.DataFrame(
      data={
        "Spot Price": summary.spot_price,
        "Call Price": summary.call_price, 
        "Put Price": summary.put_price, 
        "Call Delta": summary.greeks.delta_call,
        "Put Delta": summary.greeks.delta_put,
        "Gamma": summary.greeks.gamma,
        "Vega": summary.greeks.vega,
        "Theta Call": summary.greeks.theta_call,
        "Theta Put": summary.greeks.theta_put,
        "Rho Call": summary.greeks.rho_call,
        "Rho Put": summary.greeks.rho_put,
        }
      )
    fig = px.line(
      df,
      x = "Spot Price",
      y = ["Call Price", "Put Price"],
      title = f"Option Price Over Change in Spot {stock_name}",
      labels = {"x": "Spot Price", "y": "Option Price"}
    )

    fig.update_layout(
      yaxis_title= "Option Price",
      legend_title_text="Option Type"
    )
    st.plotly_chart(fig)

    delta_fig = px.line(
      df,
      x = "Spot Price",
      y = ["Call Delta", "Put Delta"],
      title = f"Delta Over Change in Spot {stock_name}",
      labels = {"x": "Spot Price", "y": "Delta"}
    )

    delta_fig.update_layout(
      yaxis_title= "Option Delta",
      legend_title_text="Delta Type"
    )
    st.plotly_chart(delta_fig)

    gamma_fig = px.line(
      df,
      x = "Spot Price",
      y = "Gamma",
      title = f"Gamma Over Change in Spot {stock_name}",
    )
    gamma_fig.update_layout(
      yaxis_title= "Option Gamma",
      legend_title_text="Gamma"
    )
    st.plotly_chart(gamma_fig)

    vega_fig = px.line(
      df,
      x = "Spot Price",
      y = "Vega",
      title = f"Vega Over Change in Spot {stock_name}",
    )
    vega_fig.update_layout(
      yaxis_title= "Option Vega"
    )
    st.plotly_chart(vega_fig)  

    theta_fig = px.line(
      df,
      x = "Spot Price",
      y = ["Theta Call", "Theta Put"],
      title = f"Theta Over Change in Spot {stock_name}",
    )

    theta_fig.update_layout(
      yaxis_title= "Option Theta",
      legend_title_text="Theta Type"
    )
    st.plotly_chart(theta_fig)

    rho_fig = px.line(
      df,
      x = "Spot Price",
      y = ["Rho Call", "Rho Put"],
      title = f"Rho Over Change in Spot {stock_name}",
    )
    rho_fig.update_layout(
      yaxis_title= "Option Rho",
      legend_title_text="Rho Type"
    )
    st.plotly_chart(rho_fig)

    st.dataframe(df, use_container_width=True)


