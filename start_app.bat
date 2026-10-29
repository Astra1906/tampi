@echo off
cd /d "%~dp0"
if not exist "data\processed\jolts_industry_monthly.csv" (
    echo Collecting official BLS web data and constructing the dataset...
    python main.py
    if errorlevel 1 pause & exit /b 1
)
python -m streamlit run app.py
