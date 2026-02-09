# 🌍 AI Weather Intelligence Platform

An AI-powered climate analytics and forecasting dashboard built with **Streamlit**.

## 📊 Features
- Real-time weather data using Open-Meteo API  
- 7–14 day temperature forecast using simple AI (Linear Regression)  
- Uncertainty bounds (upper and lower forecasts)  
- Micro-climate directional comparison  
- Interactive UI with charts and KPIs  
- CSV export of forecast

## 🛠 Tech Stack
- Python  
- Streamlit  
- Pandas  
- Scikit-learn  
- Open-Meteo weather API

## 📦 Installation (Local)
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
