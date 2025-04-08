@echo off

REM Kill any existing Python processes running app.py
echo Stopping any existing backend servers...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq app.py" 2>nul

REM Get the project root directory
set "PROJECT_ROOT=%~dp0.."
cd /d "%~dp0"

REM Start the backend server
echo Starting backend server...
set "PYTHONPATH=%PROJECT_ROOT%"
start /B python app.py
set "BACKEND_PID=%ERRORLEVEL%"

REM Wait a moment for the backend to start
timeout /t 2 /nobreak >nul

REM Start the frontend server
echo Starting frontend server...
cd /d "%PROJECT_ROOT%\frontend"
start /B cmd /c "S:\node.js\npm.cmd" run dev
set "FRONTEND_PID=%ERRORLEVEL%"

echo Both servers are running!
echo Backend: http://localhost:5001
echo Frontend: http://localhost:3000
echo Press Ctrl+C to stop both servers

REM Keep the window open
pause >nul

REM Cleanup on exit
taskkill /F /IM python.exe /FI "WINDOWTITLE eq app.py" 2>nul
taskkill /F /IM node.exe 2>nul 