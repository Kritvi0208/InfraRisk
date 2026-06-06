@echo off
cd /d "%~dp0"
"C:\Users\kayri\anaconda3\python.exe" -m uvicorn src.core.api_server:app --reload
