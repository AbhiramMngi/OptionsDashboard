# Stock Dashboard

A Dashboard to view prices and movements of various assets present on the S&P 500 index and price options of different styles such as :

* European
* American
* Asian (Arithmetic Mean)

Find the deployment on streamlit [here](https://optionpricerdashboard.streamlit.app/).

## Data Sources

* **yfinance** library API to obtain stock price data on the S&P 500 index.
* **portfoliolabs.com** webpages were scraped to obtain required parameters for a given stock.

## Stock Prices
* Displays the prices and volumes of a stock traded over a specified period of time.
* **YET TO IMPLEMENT** - volatility charts and analysis.

## Option Pricing 
Contains implementations of different styles of options prices, calculated on real world data and current risk free rates and dividend yields. It also provides customisability in terms of the input variables.

  ### Methods Used to Price Options
  The following methods were used to calculate the prices:

  * **Black Scholes**'s Closed form solution for European Puts and Calls.
  * **Binomial model** with incorporated dividends into price calculation for American style options.
  * **Standard Monte Carlo numerical methods** to price Asian Options with Arithmetic Mean Spot prices. 

### Greeks

**Delta**, **Gamma**, **Theta**, **Vega**, **Rho** are Implemented and plotted to view changes with respect to the changes in the price of the given stock. 

**European Options** - Closed form solutions for Greeks

**American and Asian Options** - Finite difference method to calculate the derivatives of the option with respect to input variables.




