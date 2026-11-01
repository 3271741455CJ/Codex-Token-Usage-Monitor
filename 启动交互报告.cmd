@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
set "REPORT_PYTHON=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if exist "%REPORT_PYTHON%" (
    "%REPORT_PYTHON%" -I -B "%~dp0run.py" --serve %*
) else (
    python -I -B "%~dp0run.py" --serve %*
)
if errorlevel 1 (
    echo Cannot start report. Required local packages: python-docx openpyxl Pillow reportlab.
    pause
)
