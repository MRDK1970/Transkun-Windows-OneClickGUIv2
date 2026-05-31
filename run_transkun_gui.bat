@echo off
setlocal
chcp 65001 >nul
title Transkun Windows OneClick GUI

set "ROOT=%~dp0"
cd /d "%ROOT%"

if exist "%ROOT%runtime\venv\Scripts\pythonw.exe" (
    start "" "%ROOT%runtime\venv\Scripts\pythonw.exe" "%ROOT%app\gui\transkun_gui.py" %*
    exit /b 0
)

if exist "%ROOT%runtime\venv\Scripts\python.exe" (
    start "" "%ROOT%runtime\venv\Scripts\python.exe" "%ROOT%app\gui\transkun_gui.py" %*
    exit /b 0
)

if exist "%ROOT%runtime\python\pythonw.exe" (
    start "" "%ROOT%runtime\python\pythonw.exe" "%ROOT%app\gui\transkun_gui.py" %*
    exit /b 0
)

if exist "%ROOT%runtime\python\python.exe" (
    "%ROOT%runtime\python\python.exe" "%ROOT%app\gui\transkun_gui.py" %*
    exit /b %errorlevel%
)

echo Missing bundled Python runtime.
echo Expected: %ROOT%runtime\python\pythonw.exe
pause
exit /b 1
