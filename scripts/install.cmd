@echo off
REM Bypass the machine ExecutionPolicy for this local script only.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1" %*
exit /b %ERRORLEVEL%
