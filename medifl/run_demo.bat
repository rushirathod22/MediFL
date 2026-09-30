@echo off
title MediFL Web Dashboard & FL Engine Launcher
echo ======================================================================
echo           MediFL: Enterprise Medical Federated Learning Platform
echo                       Live Web UI & FL Demo
echo ======================================================================
echo.
echo Starting MediFL FastAPI Control Server on http://localhost:8000 ...
echo Opening Web Dashboard in your browser...
echo.

start "" "http://localhost:8000/"

".\venv\Scripts\python.exe" -m uvicorn src.server.main:app --host 127.0.0.1 --port 8000

pause
