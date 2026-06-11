@echo off
cd /d "E:\TradingDashboard"

start /min cmd /c python -m streamlit run app.py --server.headless true

timeout /t 5 >nul

start http://localhost:8501