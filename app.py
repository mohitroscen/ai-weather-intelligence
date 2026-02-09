import streamlit as st
import pandas as pd
import requests
from sklearn.linear_model import LinearRegression
from datetime import timedelta
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components


# ---------------- CONFIG ---------------- #
st.set_page_config(
    page_title="AI Weather Intelligence Platform",
    page_icon="🌍",
    layout="wide"
)

st_autorefresh(interval=5 * 60 * 1000, key="weather_refresh")

# ---------------- CSS ---------------- #
st.markdown("""
<style>
.stApp {
    background: linear-gradient(rgba(0,0,0,0.65),rgba(0,0,0,0.65)),
    url("https://images.unsplash.com/photo-1501785888041-af3ef285b470");
    background-size: cover;
    background-attachment: fixed;
}

.big-title {
    font-size: 68px;
    font-weight: 800;
    color: white;
    letter-spacing: 1px;
    text-shadow: 0 6px 25px rgba(0,0,0,0.8);
    margin-bottom: 10px;
}



[data-testid="stSidebar"] {
    background: linear-gradient(270deg,#020617,#0f172a,#1e293b,#020617);
    background-size:600% 600%;
    animation: gradientFlow 18s ease infinite;
}

@keyframes gradientFlow {
    0% {background-position:0% 50%;}
    50% {background-position:100% 50%;}
    100% {background-position:0% 50%;}
}

[data-testid="metric-container"] {
    background-color: rgba(17,24,39,0.85);
    border-radius: 16px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ---------------- #
st.markdown(
    """
    <h1 class="big-title">
        🌍 AI Weather Intelligence Dashboard
    </h1>
    """,
    unsafe_allow_html=True
)

st.markdown('<p class="sub-title">Climate Risk • Forecasting • Micro-Climate Analytics</p>', unsafe_allow_html=True)
st.divider()

# ---------------- SIDEBAR ---------------- #
st.sidebar.markdown("## ⚡ Climate Command Center")

show_history = st.sidebar.toggle("📊 Show Historical Charts", True)
export = st.sidebar.button("📥 Export Forecast")

heat_threshold = st.sidebar.slider("🔥 Heatwave Threshold", 35, 45, 38)

# ---------------- CITY ---------------- #
cities = {
    "Puducherry": (11.94, 79.83),
    "Chennai": (13.08, 80.27),
    "Bangalore": (12.97, 77.59),
    "Tiruvannamalai": (12.23, 79.07),
}

city = st.sidebar.selectbox("📍 Select Region", cities.keys())
lat, lon = cities[city]

# ---------------- API ---------------- #
@st.cache_data(ttl=600)
def fetch_weather(lat, lon):
    url = (
        "https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
        "&forecast_days=14"
        "&timezone=auto"
    )
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        return r.json()
    except:
        return {"error": "API"}

data = fetch_weather(lat, lon)

# fallback
if "error" in data:
    dates = pd.date_range(end=pd.Timestamp.today(), periods=14)
    df = pd.DataFrame({
        "time": dates,
        "temperature_2m_max": [30+i*0.2 for i in range(14)],
        "temperature_2m_min": [24+i*0.1 for i in range(14)],
        "precipitation_sum": [2,4,0,10,20,0,0,4,5,0,1,0,0,3]
    })
else:
    df = pd.DataFrame(data["daily"])
    df["time"] = pd.to_datetime(df["time"])

# ---------------- KPI ---------------- #
st.subheader("📊 Climate Summary")



c1,c2,c3,c4 = st.columns(4)

c1.metric("🔥 Max Temp", f"{df['temperature_2m_max'].max():.1f}°C")
c2.metric("❄️ Min Temp", f"{df['temperature_2m_min'].min():.1f}°C")
c3.metric("🌧 Rainfall", f"{df['precipitation_sum'].sum():.0f}mm")
c4.metric("⚠️ Heat Days", len(df[df["temperature_2m_max"]>heat_threshold]))

st.divider()

st.markdown("### 🗺️ City Location (Google Maps)")

components.html(
    f"""
    <iframe
        width="100%"
        height="450"
        style="border:0"
        loading="lazy"
        allowfullscreen
        src="https://www.google.com/maps?q={lat},{lon}&z=10&output=embed">
    </iframe>
    """,
    height=450
)

# ---------------- AI FORECAST ---------------- #
st.subheader("🧠 Climate Intelligence Engine")

X = df.index.values.reshape(-1,1)
y = df["temperature_2m_max"].values

model = LinearRegression().fit(X,y)

forecast_days = st.sidebar.slider("📅 Forecast Days",3,14,7)

future_index = [[len(df)+i] for i in range(1,forecast_days+1)]
preds = model.predict(future_index)

std = (y-model.predict(X)).std()

future_dates = pd.date_range(df["time"].iloc[-1]+timedelta(days=1),
                             periods=forecast_days)

forecast_df = pd.DataFrame({
    "Date":future_dates,
    "Scenario Temp (°C)":preds,
    "Lower":preds-std,
    "Upper":preds+std
})

# risk
risk=[]
for t in forecast_df["Scenario Temp (°C)"]:
    if t>42:risk.append("Extreme")
    elif t>38:risk.append("High")
    elif t>34:risk.append("Moderate")
    else:risk.append("Low")

forecast_df["Climate Risk Level"]=risk

# ---------------- MICRO-CLIMATE ---------------- #
st.markdown("## 🧭 In-City Micro-Climate Analytics")

directions={
    "North":(lat+0.15,lon),
    "South":(lat-0.15,lon),
    "East":(lat,lon+0.15),
    "West":(lat,lon-0.15),
}

zones={}

today_temp=df["temperature_2m_max"].iloc[-1]
rain_today=df["precipitation_sum"].iloc[-1]

for zone,(zlat,zlon) in directions.items():
    zdata=fetch_weather(zlat,zlon)

    if "error" not in zdata:
        zdf=pd.DataFrame(zdata["daily"])
        zones[zone]={
            "temp":float(zdf["temperature_2m_max"].iloc[-1]),
            "rain":float(zdf["precipitation_sum"].iloc[-1]),
        }
    else:
        zones[zone]={
            "temp":today_temp+(0.8 if zone=="South" else -0.4),
            "rain":rain_today+(10 if zone=="North" else -3)
        }

# =============================
# 🌍 VISUAL MICRO-CLIMATE CARDS
# =============================

st.markdown("### 🔍 Directional Zone Climate Comparison")

temps = []

card_cols = st.columns(4)

for col, (zone, vals) in zip(card_cols, zones.items()):

    temp = vals["temp"]
    rain = vals["rain"]
    temps.append(temp)

    if rain > 30:
        label = "🌧 Rain-Dominant"
        color = "#60a5fa"
    elif temp > 38:
        label = "☀️ Hot Pocket"
        color = "#fb923c"
    elif rain > 12:
        label = "⛈ Storm Zone"
        color = "#facc15"
    else:
        label = "🌤 Stable"
        color = "#22c55e"

    col.markdown(
        f"""
        <div style="
            background:rgba(17,24,39,0.9);
            padding:22px;
            border-radius:18px;
            border-left:6px solid {color};
            box-shadow:0 0 20px rgba(0,0,0,0.6);
        ">
            <h4 style="color:white;">{zone}</h4>
            <h2 style="color:{color};">{temp:.1f} °C</h2>
            <p style="color:#d1d5db;">Rainfall: {rain:.1f} mm</p>
            <p><b>{label}</b></p>
        </div>
        """,
        unsafe_allow_html=True
    )


# ---- City-wide contrast summary ----
spread = max(temps) - min(temps)

st.markdown("### 📊 Internal Climate Contrast")

if spread > 2:
    st.warning(
        f"⚠️ **Strong micro-climate variation detected inside {city}.** "
        f"Temperature difference ≈ {spread:.2f} °C."
    )
else:
    st.success(
        f"✅ **Uniform conditions across {city}.** "
        f"Temperature difference ≈ {spread:.2f} °C."
    )

st.divider()

# ---------------- VISUAL ---------------- #
st.markdown("### 📊 Forecast")

st.line_chart(
    forecast_df.set_index("Date")[[
        "Scenario Temp (°C)","Lower","Upper"
    ]]
)

st.markdown("### 📋 Forecast Table")
st.dataframe(forecast_df)

# ---------------- EXPORT ---------------- #
if export:
    st.sidebar.download_button(
        "⬇️ Download CSV",
        forecast_df.to_csv(index=False).encode(),
        f"{city}_forecast.csv"
    )

# ---------------- FOOTER ---------------- #
st.markdown("""
### 🌱 Sustainability Impact

• Detect internal city climate zones  
• Support adaptation plans  
• Identify flood/heat pockets  
• Urban resilience modelling  

**Next Phase**
• AQI  
• Flood risk  
• Satellite layers  
• Carbon analytics  
""")
