@echo off
title ROVO AI Car Rental
echo Installing required Python packages...
python -m pip install -r requirements.txt
echo.
echo Starting ROVO at http://127.0.0.1:5000
python app.py
pause
