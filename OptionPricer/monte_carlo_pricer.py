import numpy as np
from utils.utils import OptionSummary, Greeks

class MonteCarloAsianOptionPricer:
  def summary(
      self,
      sec_obj
  ):
    n_simulations = 10000
    time_to_maturity = int(sec_obj.time_to_expiration * 365)
    K = sec_obj.strike_price
    rate = sec_obj.risk_free_rate
    sig = sec_obj.volatility
    avg_start_date = sec_obj.average_start_date
    avg_end_date = sec_obj.average_end_date
    S = sec_obj.spot_price
    def option_prices(r, sigma, spot, ttm):
      

      n_days = (avg_end_date - avg_start_date).days + 1
      dt = np.array([1/365 for i in range(ttm)])
      time_sum = np.cumsum(dt)
      sqrt_time_sum = np.cumsum(np.sqrt(dt) * np.random.normal(size=(n_simulations, dt.shape[0])), axis = 1)
      drift = (r - (0.5 * sigma) ** 2) * time_sum
      vol = (sigma) * sqrt_time_sum
      print(vol.shape, drift.shape, sqrt_time_sum.shape)
      S_t = spot * np.exp(drift + vol)

      A_t = S_t[:, (-ttm+ n_days):].mean(axis=1)
      C_t = (np.maximum(A_t - K, 0) * np.exp(-r * (ttm/365))).mean()
      P_t = (np.maximum(K - A_t, 0) * np.exp(-r * (ttm/365))).mean()

      return C_t, P_t
    
    def greeks(spot):
      call_old_price, put_old_price = option_prices(rate, sig, spot - 0.01, time_to_maturity)
      call_price, put_price = option_prices(rate, sig, spot, time_to_maturity)
      call_new_price, put_new_price = option_prices(rate, sig, spot + 0.01, time_to_maturity)
      delta_call = (call_price - call_new_price)/(-0.01)
      delta_put = (put_price - put_new_price)/(-0.01)
      delta_old_put = (put_old_price - put_price)/ (-0.01)
      delta_old_call = (call_old_price - call_price)/ (-0.01)
      
      gamma = (delta_call - delta_old_call)/(-0.02)

      call_price, put_price = option_prices(rate, sig, spot, time_to_maturity)
      call_new_price, put_new_price = option_prices(rate, sig + 0.01, spot, time_to_maturity)
      vega = (call_new_price - call_price)/(-0.01)

      call_price, put_price = option_prices(rate, sig, spot, time_to_maturity)
      call_new_price, put_new_price = option_prices(rate, sig, spot, time_to_maturity + 1)
      theta_call = (call_new_price - call_price)
      theta_put = (put_new_price - put_price)

      call_price, put_price = option_prices(rate, sig, spot, time_to_maturity)
      call_new_price, put_new_price = option_prices(rate + 0.01, sig, spot, time_to_maturity)

      rho_call = (call_new_price - call_price) / (-0.01)
      rho_put = (put_new_price - put_price)/(-0.01)

      return Greeks(
        delta_call/100,
        delta_put/100,
        gamma/100,
        vega/100,
        theta_call/365,
        theta_put/365,
        rho_call/100,
        rho_put/100
      )

    call_prices, put_prices = [], []
    gre = Greeks([],[],[],[],[],[],[],[])
    for spot in np.arange(0, S * 2, S/10):

      call_price, put_price= option_prices(r=rate, sigma=sig,spot=spot, ttm=time_to_maturity)
      call_prices.append(call_price)
      put_prices.append(put_price)

      g = greeks(spot)
      gre.delta_call.append(g.delta_call)
      gre.delta_put.append(g.delta_put)
      gre.gamma.append(g.gamma)
      gre.vega.append(g.vega)
      gre.theta_call.append(g.theta_call)
      gre.theta_put.append(g.theta_put)
      gre.rho_call.append(g.rho_call)
      gre.rho_put.append(g.rho_put)

    return OptionSummary(
      sec_obj.stock_ticker,
      np.arange(0, S * 2, S/10),
      sec_obj.risk_free_rate,
      sec_obj.volatility,
      sec_obj.time_to_expiration,
      sec_obj.dividend_rate,
      sec_obj.strike_price,
      call_prices,
      put_prices,
      gre
    )
  


    









