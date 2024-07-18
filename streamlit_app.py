import streamlit as st
from StockTicker.stock_ticker import render_stock_data
from OptionPricer.option_pricer import render_option_dashboard

st.session_state.flag = True



page = st.selectbox(
  "Select Page",
  ("Stock Price Dashboard","Option Price Dashboard"),
  index=0,
  placeholder="Select Page"
)


if page == "Stock Price Dashboard":
  st.title("Stock Price Dashboard")
  render_stock_data()
elif page == "Option Price Dashboard":
  st.title("Option Price Dashboard")
  render_option_dashboard()

  
      


