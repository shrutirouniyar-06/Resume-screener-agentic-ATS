@echo off
REM Screen-U Quick Start Script for Windows

echo.
echo ======================================
echo  Screen-U Backend ^& Frontend Startup
echo ======================================
echo.

REM Start Backend
echo [1/2] Starting Flask Backend...
cd backend
start "Screen-U Backend" python app.py
timeout /t 3 /nobreak

REM Check if backend is running
for /f "tokens=*" %%i in ('curl -s http://localhost:5000/api/health 2^>nul') do (
    if not "%%i"=="" (
        echo [OK] Backend running on http://localhost:5000
        goto backend_ok
    )
)
echo [ERROR] Backend failed to start. Check .env file and API keys.
pause
exit /b 1

:backend_ok
REM Start Frontend
echo.
echo [2/2] Starting React Frontend...
cd ..\frontend
start "Screen-U Frontend" npm run dev
timeout /t 5 /nobreak

echo.
echo ======================================
echo  SERVERS RUNNING!
echo ======================================
echo.
echo Frontend:  http://localhost:5173
echo Backend:   http://localhost:5000
echo.
echo Open http://localhost:5173 in your browser!
echo.
pause
