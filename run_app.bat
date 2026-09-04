@echo off
title FutureMining Launcher
echo ========================================================
echo    FutureMining - GATE Mining Preparation Platform
echo    FastAPI Backend + Supabase PostgreSQL + Streamlit UI
echo ========================================================
echo.

echo [1/2] Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "FutureMining FastAPI Backend" cmd /k "cd backend && python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload"

timeout /t 3 /nobreak >nul

echo [2/2] Starting Streamlit Frontend on http://localhost:8501 ...
python -m streamlit run app.py

pause
