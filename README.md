<img width="1512" height="982" alt="Screenshot 2026-02-09 at 8 25 47 PM" src="https://github.com/user-attachments/assets/7f1c7d0b-472c-47c8-8d22-6a93c5fb4e89" /># 🌍 AI Weather Intelligence Platform

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
