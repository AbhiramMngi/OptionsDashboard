import streamlit as st
from StockTicker.stock_ticker import render_stock_data

with st.sidebar:
  page = st.selectbox(
    "Select Page",
    ("Price Dashboard",""),
    index=None,
    placeholder="Select Page"
  )

if page == "Price Dashboard":
  render_stock_data()
      


