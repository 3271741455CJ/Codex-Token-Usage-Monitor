@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
if /i not "%~1"=="--no-open" (
    call "%~dp0启动交互报告.cmd" %*
    exit /b
)
where py.exe >nul 2>nul
if not errorlevel 1 (
    py.exe -3 -I -S -B "%~dp0run.py"
    if errorlevel 1 goto failed
    goto show
)
where python.exe >nul 2>nul
if not errorlevel 1 (
    python.exe -I -S -B "%~dp0run.py"
    if errorlevel 1 goto failed
    goto show
)
echo Please install Python 3.11+ locally. This project never downloads dependencies.
goto failed
:show
if /i "%~1"=="--no-open" exit /b 0
start "" "%~dp0.reports\latest.html"
exit /b 0
:failed
echo Report generation failed. See the message above.
if /i "%~1"=="--no-open" exit /b 1
pause
exit /b 1
