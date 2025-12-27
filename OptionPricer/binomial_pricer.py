import numpy as np 
from utils.utils import Greeks, OptionSummary

class BinomialAmericanOptionPricer:
  def summary(
      self,
      sec_obj
  ):
    n_steps = 200
    dt = sec_obj.time_to_expiration / n_steps
    K = sec_obj.strike_price
    r = sec_obj.risk_free_rate
    sigma = sec_obj.volatility
    T = sec_obj.time_to_expiration
    def option_prices(spot_price, r, vol):

      u = np.exp(vol * np.sqrt(dt))
      d = 1 / u
      p = (np.exp(r * dt) - d) / (u - d)
      S = np.array([[(d ** (j - i)) * (u ** i) * (1 - sec_obj.dividend_rate*np.exp(-r * j * dt)) if j >= i else 0 for i in range(n_steps + 1)]for j in range(n_steps + 1)]) * spot_price

      call_payoffs = np.maximum(S.copy() - K, 0)

      for i in range(n_steps - 1, -1, -1):
        for j in range(i + 1):
          call_payoffs[i, j] = max(call_payoffs[i, j], np.exp(-r * dt) * (p * call_payoffs[i + 1,j + 1] + (1 - p) * call_payoffs[i + 1, j]))

      put_payoffs = np.maximum(K - S.copy(), 0)

      for i in range(n_steps - 1, -1, -1):
        for j in range(i + 1):
          put_payoffs[i, j] = max(put_payoffs[i, j], np.exp(-r * dt) * ((1 - p) * put_payoffs[i + 1, j] + p * put_payoffs[i + 1, j + 1]))

      return call_payoffs, put_payoffs, S
    
    def greeks(spot):
      calls, puts, S = option_prices(r=r, vol=sigma,spot_price=spot)
      delta_call = (calls[1, 0] - calls[1, 1])/(S[1, 0] - S[1, 1])
      delta_put = (puts[1, 0] - puts[1, 1])/(S[1, 0] - S[1, 1])
      delta_up = (calls[2, 0] - calls[2, 1]) / (S[2, 0] - S[2, 1])
      delta_down = (calls[2, 1] - calls[2, 2]) / (S[2, 1] - S[2, 2])
      gamma = (delta_up - delta_down) / (0.5 * (S[2, 0] - S[2, 2]))
      
      # Interpolated Theta Calculation
      s_down = S[1, 0]
      s_up = S[1, 1]
      
      # Call Theta
      c_down = calls[1, 0]
      c_up = calls[1, 1]
      if s_up != s_down:
          c_dt = (c_up * (spot - s_down) + c_down * (s_up - spot)) / (s_up - s_down)
      else:
          c_dt = c_down
      theta_call = (c_dt - calls[0, 0]) / dt
      
      # Put Theta
      p_down = puts[1, 0]
      p_up = puts[1, 1]
      if s_up != s_down:
          p_dt = (p_up * (spot - s_down) + p_down * (s_up - spot)) / (s_up - s_down)
      else:
          p_dt = p_down
      theta_put = (p_dt - puts[0, 0]) / dt

      calls, puts, S = option_prices(r = r - 0.01, vol = sigma, spot_price=spot)
      calls_new, puts_new, S = option_prices(r=r+0.01, vol=sigma, spot_price=spot)
      rho_call = (calls_new[0, 0] - calls[0, 0]) / 0.02
      rho_put = (puts_new[0, 0] - puts[0, 0]) / 0.02
      calls, puts, S = option_prices(r = r, vol = sigma - 0.01, spot_price=spot)
      calls_new, puts_new, S = option_prices(r=r, vol=sigma + 0.01, spot_price=spot)
      vega = (calls_new[0, 0] - calls[0, 0]) / (0.02)

      return Greeks(
        delta_call,
        delta_put,
        gamma, 
        vega/100,
        theta_call/365,
        theta_put/365,
        rho_call/100,
        rho_put/100
      )
    
    call_prices, put_prices = [], []
    gre = Greeks([],[],[],[],[],[],[],[])
    
    # Use local variable for spot prices
    spot_prices = np.arange(0, sec_obj.spot_price * 2, sec_obj.spot_price/10)
    
    for spot in spot_prices:

      call_price, put_price, S = option_prices(r=r, vol=sigma,spot_price=spot)
      call_prices.append(call_price[0, 0])
      put_prices.append(put_price[0, 0])


      g = greeks(spot)
      gre.delta_call.append(g.delta_call)
      gre.delta_put.append(g.delta_put)
      gre.gamma.append(g.gamma)
      gre.vega.append(g.vega)
      
      # Recalculate Theta using interpolation for better accuracy
      # The greeks() function uses a simpler approximation, we override it here or fix it inside greeks()
      # Let's fix it inside greeks() actually, to be cleaner.
      # But greeks() is defined above. I will modify greeks() definition in the next block.
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