@echo off
title MediFL Automated Verification & Test Suite
echo ======================================================================
echo           MediFL: Enterprise Medical Federated Learning Platform
echo                     Automated Test Suite Runner
echo ======================================================================
echo.
echo Running Unit and Integration Tests via pytest...
echo.

".\venv\Scripts\python.exe" -m pytest tests/ -v

echo.
echo ======================================================================
echo Test execution complete.
echo ======================================================================
pause
