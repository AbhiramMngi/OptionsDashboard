import numpy as np
from datetime import date
import re
import yfinance as yf
import pandas as pd

securities = [i[0] for i in pd.read_csv('securities.csv').values.tolist()]

class OptionSummary:
  def __init__(
    self,
    stock_ticker,
    spot_price,
    risk_free_rate,
    volatility,
    time_to_expiration,
    dividend_rate,
    strike_price,
    call_price,
    put_price,
    greeks
  ):
    self.stock_ticker = stock_ticker
    self.spot_price = spot_price
    self.risk_free_rate = risk_free_rate
    self.volatility = volatility  
    self.time_to_expiration = time_to_expiration
    self.dividend_rate = dividend_rate
    self.strike_price = strike_price
    self.call_price = call_price
    self.put_price = put_price
    self.greeks = greeks
    

class Greeks:
  def __init__(
    self,
    delta_call,
    delta_put,
    gamma,
    vega,
    theta_call,
    theta_put,
    rho_call,
    rho_put
  ):
    self.delta_call = delta_call
    self.delta_put = delta_put
    self.gamma = gamma
    self.vega = vega
    self.theta_call = theta_call
    self.theta_put = theta_put
    self.rho_call = rho_call
    self.rho_put = rho_put


class PricerInput:
  def __init__(
    self,
    stock_ticker,
    option_style,
    spot_price,
    strike_price,
    risk_free_rate,
    volatility,
    expiration_date,
    dividend_rate,
    average_start_date = None,
  ): 
    self.stock_ticker = stock_ticker
    self.spot_price = spot_price
    self.strike_price = strike_price
    self.risk_free_rate = np.log(1 + risk_free_rate/100.0)
    self.dividend_rate = np.log(1 + dividend_rate/100.0)
    self.volatility = volatility/100.0
    self.time_to_expiration = (expiration_date - date.today()).days/365
    if self.time_to_expiration == 0:
      self.time_to_expiration = 1e-4
    self.average_start_date = average_start_date
    self.average_end_date = expiration_date


def extract_security_name(sec):
  return re.match(r'^(.*) \((.*)\)$', sec).group(2)

def calculate_stock_volatility(sec, days):
  sec = extract_security_name(sec)
  data = yf.download([sec], period="5y", interval="1d")
  vol = pd.DataFrame()
  vol["vol"] = data["Close"].pct_change().rolling(window=days).std()
  vol["date"] = data.index
  return vol

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
  return data.info.get('dividendYield', 0.0) / 100

def continuous_rate(rate):
  return np.log(1 + rate)