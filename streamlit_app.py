import streamlit as st
from StockTicker.stock_ticker import render_stock_data

st.session_state.flag = True

with st.sidebar:
  page = st.selectbox(
    "Select Page",
    ("Stock Price Dashboard",""),
    index=0,
    placeholder="Select Page"
  )


st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        width: 42%;
    }
    </style>
    """,
    unsafe_allow_html=True
)



if page == "Stock Price Dashboard":
  st.title("Stock Price Dashboard")
  render_stock_data()
      


