import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Page config
st.set_page_config(page_title="Stock Dashboard", layout="wide")
st.title("📈 Stock Price Dashboard")

# Fetch data with comprehensive error handling and retry logic
@st.cache_data
def fetch_stock_data(ticker, days=90):
    """Fetch stock/crypto data with retry logic and detailed error reporting"""
    max_retries = 3
    retry_count = 0

    while retry_count < max_retries:
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            # Download data with detailed settings
            data = yf.download(
                ticker,
                start=start_date,
                end=end_date,
                progress=False,
                timeout=30
            )

            # Validate data is not empty
            if data is None or data.empty:
                retry_count += 1
                if retry_count < max_retries:
                    continue
                st.error(f"No data returned for {ticker} after {max_retries} attempts. Check ticker symbol or try refreshing.")
                return pd.DataFrame()

            # Validate Close column exists and has data
            if 'Close' not in data.columns:
                st.error(f"Close column missing for {ticker}. Data structure issue.")
                return pd.DataFrame()

            return data

        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                st.error(f"Error fetching {ticker}: {str(e)}")
                return pd.DataFrame()
            continue

    return pd.DataFrame()

# Helper function to safely extract latest price
def get_latest_price(data, ticker):
    """Safely extract latest close price with comprehensive edge case handling"""
    try:
        if data is None or data.empty:
            return None

        # Get the Close column
        close_col = data['Close']

        # Handle case where Close might be a DataFrame (multi-level columns)
        if isinstance(close_col, pd.DataFrame):
            close_col = close_col.iloc[:, 0]

        # Verify the series is not empty
        if len(close_col) == 0:
            return None

        # Get the last non-NaN value, in case the very last value is NaN
        for i in range(len(close_col) - 1, -1, -1):
            val = close_col.iloc[i]

            # Skip NaN values
            if pd.isna(val):
                continue

            # Convert to float
            try:
                latest_value = float(val)
                # Final check for NaN
                if np.isnan(latest_value):
                    continue
                return latest_value
            except (ValueError, TypeError):
                continue

        # No valid values found
        return None

    except (KeyError, IndexError, TypeError, ValueError, AttributeError) as e:
        st.warning(f"Could not extract price for {ticker}: {str(e)}")
        return None

# Create tabs
tab1, tab2 = st.tabs(["Stock Tracker", "Crypto Tracker"])

# STOCK TRACKER TAB
with tab1:
    # Load data for both stocks
    aapl_data = fetch_stock_data("AAPL")
    googl_data = fetch_stock_data("GOOGL")

    # Validate data before proceeding
    if aapl_data.empty or googl_data.empty:
        st.warning("Unable to load stock data. Please check your connection and refresh.")
    else:
        # Create figure with both stocks
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=aapl_data.index,
            y=aapl_data['Close'],
            mode='lines',
            name='AAPL',
            line=dict(color='#1f77b4', width=2)
        ))

        fig.add_trace(go.Scatter(
            x=googl_data.index,
            y=googl_data['Close'],
            mode='lines',
            name='GOOGL',
            line=dict(color='#ff7f0e', width=2)
        ))

        fig.update_layout(
            title="AAPL vs GOOGL (Last 90 Days)",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            hovermode='x unified',
            template='plotly_white',
            height=600
        )

        st.plotly_chart(fig, use_container_width=True)

        # Display latest prices using helper function
        col1, col2 = st.columns(2)

        aapl_price = get_latest_price(aapl_data, "AAPL")
        googl_price = get_latest_price(googl_data, "GOOGL")

        with col1:
            if aapl_price is not None:
                st.metric("AAPL Latest Close", f"${aapl_price:.2f}")
            else:
                st.warning("AAPL price data unavailable")

        with col2:
            if googl_price is not None:
                st.metric("GOOGL Latest Close", f"${googl_price:.2f}")
            else:
                st.warning("GOOGL price data unavailable")

# CRYPTO TRACKER TAB
with tab2:
    # Load data for both cryptos
    btc_data = fetch_stock_data("BTC-USD")
    eth_data = fetch_stock_data("ETH-USD")

    # Validate data before proceeding
    if btc_data.empty or eth_data.empty:
        st.warning("Unable to load crypto data. Please check your connection and refresh.")
    else:
        # Create figure with both cryptos
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=btc_data.index,
            y=btc_data['Close'],
            mode='lines',
            name='BTC',
            line=dict(color='#f7931a', width=2)
        ))

        fig.add_trace(go.Scatter(
            x=eth_data.index,
            y=eth_data['Close'],
            mode='lines',
            name='ETH',
            line=dict(color='#627eea', width=2)
        ))

        fig.update_layout(
            title="BTC vs ETH (Last 90 Days)",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            hovermode='x unified',
            template='plotly_white',
            height=600
        )

        st.plotly_chart(fig, use_container_width=True)

        # Display latest prices using helper function
        col1, col2 = st.columns(2)

        btc_price = get_latest_price(btc_data, "BTC")
        eth_price = get_latest_price(eth_data, "ETH")

        with col1:
            if btc_price is not None:
                st.metric("BTC Latest Close", f"${btc_price:.2f}")
            else:
                st.warning("BTC price data unavailable")

        with col2:
            if eth_price is not None:
                st.metric("ETH Latest Close", f"${eth_price:.2f}")
            else:
                st.warning("ETH price data unavailable")
