@echo off
setlocal
chcp 65001 >nul
title Transkun Windows OneClick

set "ROOT=%~dp0"
cd /d "%ROOT%"

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%ROOT%run_transkun.ps1" %*
if errorlevel 1 (
    echo.
    echo Transkun failed or was cancelled.
    echo Please check the logs folder for details.
    echo.
    pause
    exit /b 1
)

echo.
pause
exit /b 0
