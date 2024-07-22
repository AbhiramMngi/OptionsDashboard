import numpy as np
from scipy.stats import norm
from utils.utils import OptionSummary, Greeks

class BlackScholesPricer:
  def summary(
    self,
    sec_obj
  ):
    sec_obj.spot_price = np.arange(sec_obj.spot_price * 0, sec_obj.spot_price * 2, sec_obj.spot_price * 0.1)
    
    def ds():
      d1 = (np.log(sec_obj.spot_price/sec_obj.strike_price) + (sec_obj.risk_free_rate - sec_obj.dividend_rate + (sec_obj.volatility**2)/2) * sec_obj.time_to_expiration)/(sec_obj.volatility * np.sqrt(sec_obj.time_to_expiration))
      d2 = d1 - sec_obj.volatility * np.sqrt(sec_obj.time_to_expiration)
      return d1, d2
    
    def option_prices():
      d1, d2 = ds()
      call_price = sec_obj.spot_price * np.exp(-sec_obj.dividend_rate * sec_obj.time_to_expiration) * norm.cdf(d1) - sec_obj.strike_price * np.exp(-sec_obj.risk_free_rate * sec_obj.time_to_expiration) * norm.cdf(d2)
      put_price = sec_obj.strike_price * np.exp(-sec_obj.risk_free_rate * sec_obj.time_to_expiration) * norm.cdf(-d2) - sec_obj.spot_price * np.exp(-sec_obj.dividend_rate * sec_obj.time_to_expiration) * norm.cdf(-d1)
      return call_price, put_price
    
    def greeks():
      d1, d2 = ds()
      dividend_discount = np.exp(-sec_obj.dividend_rate * sec_obj.time_to_expiration)
      risk_free_discount = np.exp(-sec_obj.risk_free_rate * sec_obj.time_to_expiration)

      delta_call = dividend_discount * norm.cdf(d1)
      delta_put =  dividend_discount*(norm.cdf(d1) - 1)
      gamma = (dividend_discount * norm.pdf(d1)) / (sec_obj.spot_price * sec_obj.volatility * np.sqrt(sec_obj.time_to_expiration))
      vega = sec_obj.spot_price * dividend_discount * np.sqrt(sec_obj.time_to_expiration) * norm.pdf(d1)/100

      theta_call = (1/sec_obj.time_to_expiration) * (
        -sec_obj.spot_price * dividend_discount * sec_obj.volatility * norm.pdf(d1) / (2 * np.sqrt(sec_obj.time_to_expiration)) - 
        sec_obj.risk_free_rate * sec_obj.strike_price * risk_free_discount * norm.cdf(d2) + 
        sec_obj.dividend_rate * sec_obj.spot_price * dividend_discount * norm.cdf(d1)
      )
      theta_put = (1/sec_obj.time_to_expiration) * (
        -sec_obj.spot_price * dividend_discount * sec_obj.volatility * norm.pdf(d1) / (2 * np.sqrt(sec_obj.time_to_expiration)) + 
        sec_obj.risk_free_rate * sec_obj.strike_price * risk_free_discount * norm.cdf(-d2) -
        sec_obj.dividend_rate * sec_obj.spot_price * dividend_discount * norm.cdf(-d1)
      )

      rho_call = sec_obj.strike_price * sec_obj.time_to_expiration * risk_free_discount * norm.cdf(d2)/100
      rho_put = -sec_obj.strike_price * sec_obj.time_to_expiration * risk_free_discount * norm.cdf(-d2)/100

      return Greeks(
        delta_call,
        delta_put,
        gamma,
        vega,
        theta_call/365,
        theta_put/365,
        rho_call,
        rho_put
      )
    
    call_price, put_price = option_prices()
    return OptionSummary(
      sec_obj.stock_ticker,
      sec_obj.spot_price,
      sec_obj.risk_free_rate,
      sec_obj.volatility,
      sec_obj.time_to_expiration,
      sec_obj.dividend_rate,
      sec_obj.strike_price,
      call_price,
      put_price,
      greeks()
    )

               