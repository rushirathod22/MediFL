@echo off
title MediFL Multi-Hospital FL Terminal Simulator
echo ======================================================================
echo           MediFL: Multi-Hospital Federated Learning Simulator
echo            Simulating 3 Hospital Nodes (Mumbai, Pune, Delhi)
echo ======================================================================
echo.

".\venv\Scripts\python.exe" -m src.aggregator.simulator

echo.
echo ======================================================================
echo Simulation run finished.
echo ======================================================================
pause
