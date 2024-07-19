import numpy as np
from OptionPricer.utils.utils import OptionSummary, Greeks

class MonteCarloAsianOptionPricer:
  def summary(
      self,
      sec_obj
  ):
    n_simulations = 100
    ttm = int(sec_obj.time_to_expiration * 365)
    K = sec_obj.strike_price
    rate = sec_obj.risk_free_rate
    sig = sec_obj.volatility
    avg_start_date = self.average_start_date
    avg_end_date = self.average_end_date
    S = self.spot_price
    def option_prices(r, sigma, spot):
      

      n_days = (avg_end_date - avg_start_date + 1).days
      dt = np.array([1/365 for i in range(ttm)])
      time_sum = np.cumsum(dt)
      sqrt_time_sum = np.cumsum(np.sqrt(dt) * np.random.normal(size=(n_simulations, dt.shape[0])))
      drift = (r - (0.5 * sigma) ** 2) * time_sum
      vol = (sigma) * sqrt_time_sum
      
      S_t = spot * np.exp(drift + vol)

      A_t = S_t[:, (-ttm+ n_days):].mean(axis=1)
      C_t = np.maximum(A_t - K, 0) * np.exp(-r * (ttm/365))
      P_t = np.maximum(K - A_t, 0) * np.exp(-r * (ttm/365))

      return C_t, P_t
    
    def greeks():
      
      pass

    call_prices, put_prices = [], []
    gre = Greeks([],[],[],[],[],[],[],[])
    for spot in np.arange(0, sec_obj.spot_price * 2, sec_obj.spot_price/10):

      call_price, put_price, S = option_prices(r=rate, vol=sig,spot_price=spot)
      call_prices.append(call_price[0, 0])
      put_prices.append(put_price[0, 0])

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
      sec_obj.spot_price,
      sec_obj.risk_free_rate,
      sec_obj.volatility,
      sec_obj.time_to_expiration,
      sec_obj.dividend_rate,
      sec_obj.strike_price,
      call_prices,
      put_prices,
      gre
    )
  


    









