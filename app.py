import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import google.generativeai as genai

# --- CONFIG & THEME ---
st.set_page_config(page_title="SPX Terminal", layout="centered")

# Custom CSS for "Terminal" Look
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #000000; color: #00FF00; }
    .stMetric { background-color: #111; border: 1px solid #333; padding: 10px; border-radius: 5px; }
    div[data-testid="metric-container"] { color: white !important; }
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    </style>
    """, unsafe_allow_html=True)

# --- AI SETUP ---
# This pulls your key from the "Secrets" we will set up later
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# --- DATA FETCHING ---
@st.cache_data(ttl=3600)
def get_market_data():
    # This header helps bypass the Yahoo "Rate Limit" block
    import requests
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0'})
    
    spy = yf.Ticker("SPY", session=session)
    df = spy.history(period="1mo")
    return df


data = get_market_data()
latest_price = data['Close'].iloc[-1]
prev_price = data['Close'].iloc[-2]
diff = latest_price - prev_price

# --- UI LAYOUT ---
st.title("📟 SPX_INTELLIGENCE_v1")
cols = st.columns(2)
cols[0].metric("S&P 500 (SPY)", f"${latest_price:.2f}", f"{diff:.2f}")
cols[1].metric("VOLATILITY (VIX)", "18.42", "-1.2%") 

st.subheader("🤖 AI Market Signal")
with st.container():
    context = f"SPY is at {latest_price}. Recent trend is {'Up' if diff > 0 else 'Down'}."
    if st.button("RUN AI DEEP DIVE"):
        analysis = model.generate_content(f"Analyze S&P 500 state: {context}. Give a 3-bullet point summary for a pro trader on mobile.")
        st.markdown(analysis.text)
    else:
        st.info("Tap 'Run AI' for the latest sentiment analysis.")

st.subheader("📈 Technicals")
fig = go.Figure(data=[go.Candlestick(x=data.index,
                open=data['Open'], high=data['High'],
                low=data['Low'], close=data['Close'])])

fig.update_layout(
    template="plotly_dark",
    xaxis_rangeslider_visible=False,
    margin=dict(l=10, r=10, t=10, b=10),
    height=300 
)
st.plotly_chart(fig, use_container_width=True)

st.caption("KEYWORDING: #AI_CHIPS #FED_PIVOT #LIQUIDITY_GAP")
