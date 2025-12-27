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
    # Pre-generate random numbers for Common Random Numbers (CRN) technique
    # We need enough steps for time_to_maturity + 1 (for Theta calculation)
    max_steps = time_to_maturity + 2
    Z = np.random.normal(size=(n_simulations, max_steps))
    
    def option_prices(r, sigma, spot, ttm, z_matrix=None):
      
      n_days = (avg_end_date - avg_start_date).days + 1
      dt = np.array([1/365 for i in range(ttm)])
      
      # Use provided Z matrix or generate new one (should always be provided for Greeks)
      if z_matrix is not None:
          current_z = z_matrix[:, :ttm]
      else:
          current_z = np.random.normal(size=(n_simulations, ttm))
          
      # Construct Brownian path
      # dW = sqrt(dt) * Z
      # W = cumsum(dW)
      # But the original code did: cumsum(sqrt(dt) * Z) which is correct for W_t
      
      # Note: The original code calculated 'sqrt_time_sum' which seems to be the Brownian Motion W_t
      # sqrt_time_sum = np.cumsum(np.sqrt(dt) * np.random.normal(...))
      
      sqrt_dt = np.sqrt(dt)
      # Broadcast sqrt_dt to shape of current_z if needed, but here it's 1D array of length ttm
      # We need to multiply each column j by sqrt_dt[j]
      
      dW = current_z * sqrt_dt
      W_t = np.cumsum(dW, axis=1)
      
      time_sum = np.cumsum(dt)
      
      drift = (r - 0.5 * sigma ** 2) * time_sum
      vol = (sigma) * W_t
      # print(vol.shape, drift.shape, W_t.shape)
      S_t = spot * np.exp(drift + vol)

      A_t = S_t[:, (-ttm+ n_days):].mean(axis=1)
      C_t = (np.maximum(A_t - K, 0) * np.exp(-r * (ttm/365))).mean()
      P_t = (np.maximum(K - A_t, 0) * np.exp(-r * (ttm/365))).mean()

      return C_t, P_t
    
    def greeks(spot):
      # Use the same Z matrix for all price calculations for this spot to ensure smooth Greeks
      
      call_old_price, put_old_price = option_prices(rate, sig, spot - 0.01, time_to_maturity, Z)
      call_price, put_price = option_prices(rate, sig, spot, time_to_maturity, Z)
      call_new_price, put_new_price = option_prices(rate, sig, spot + 0.01, time_to_maturity, Z)
      
      delta_call = (call_new_price - call_price)/(0.01)
      delta_put = (put_new_price - put_price)/(0.01)
      
      gamma = (call_new_price - 2*call_price + call_old_price) / (0.01**2)

      # Vega: change in vol. Use same Z.
      call_vol_up, put_vol_up = option_prices(rate, sig + 0.01, spot, time_to_maturity, Z)
      vega = (call_vol_up - call_price)/(0.01)

      # Theta: change in time. Use Z (it will slice differently but use same underlying numbers)
      call_time_up, put_time_up = option_prices(rate, sig, spot, time_to_maturity + 1, Z)
      theta_call = (call_price - call_time_up)
      theta_put = (put_price - put_time_up)

      # Rho: change in rate. Use same Z.
      call_rate_up, put_rate_up = option_prices(rate + 0.01, sig, spot, time_to_maturity, Z)

      rho_call = (call_rate_up - call_price) / (0.01)
      rho_put = (put_rate_up - put_price)/(0.01)

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
    
    spot_prices = np.arange(0, S * 2, S/10)
    
    for spot in spot_prices:

      call_price, put_price= option_prices(r=rate, sigma=sig,spot=spot, ttm=time_to_maturity, z_matrix=Z)
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
      spot_prices,
      sec_obj.risk_free_rate,
      sec_obj.volatility,
      sec_obj.time_to_expiration,
      sec_obj.dividend_rate,
      sec_obj.strike_price,
      call_prices,
      put_prices,
      gre
    )
  


    









