@echo off
echo Restarting backend...
cd backend
taskkill /F /IM python.exe /FI "WINDOWTITLE eq backend*" 2>nul
timeout /t 2 /nobreak >nul
start "backend" python app.py
echo Backend restarted!
