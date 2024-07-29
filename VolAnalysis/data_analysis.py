import yfinance as yf
import pandas as pd
from utils.utils import extract_security_name
import numpy as np
from scipy.optimize import minimize
from scipy.stats import norm
import streamlit as st

    
def black_scholes(x, data):
  # st.write(data["ttm"])
  def ds():
    t1 = ((data["risk_free_rate"] - data["dividend_rate"] + (x**2)/2) * data["ttm"]).values
    t2 = np.log(data["spot_price"]/data["strike"]).values
    d1 = (t1 + t2)/(x * np.sqrt(data["ttm"]))
    d2 = d1 - x * np.sqrt(data["ttm"])
    return d1, d2
  d1, d2 = ds()
  call_price = data["spot_price"] * np.exp(-data["dividend_rate"] * data["ttm"]) * norm.cdf(d1) - data["strike"] * np.exp(-data["risk_free_rate"] * data["ttm"]) * norm.cdf(d2)
  # st.write(call_price)
  # st.write(call_price.shape)
  return call_price

def fetch_option_data(sec, spot_price):
  if sec is None:
    sec = "AAPL"
  sec = extract_security_name(sec)
  ticker = yf.Ticker(sec)
  expiry_dates = ticker.options

  def fetch_options_data(date):
    data = ticker.option_chain(date)
    call_data = data.calls[["strike", "lastPrice", "impliedVolatility"]]
    call_data["expiry_date"] = pd.to_datetime(date)
    return call_data
  
  fetch_options = np.vectorize(fetch_options_data)

  options_data = pd.concat(fetch_options(expiry_dates), ignore_index=True)

  options_data["ttm"] = (options_data["expiry_date"] - pd.Timestamp(0)).dt.days/365
  options_data["spot_price"] = spot_price
  return options_data


def calculate_implied_volatility(data):
  def objective_function(volatility):
    return np.sum((data["lastPrice"] - black_scholes(volatility, data))**2)
  
  results = minimize(objective_function, np.ones_like(data["lastPrice"])*0.05, method="Nelder-Mead", bounds=[[0.0, None]])
  st.write("Bye")
  return results.x



  


  
