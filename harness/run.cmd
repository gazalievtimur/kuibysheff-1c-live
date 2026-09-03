@echo off
REM Bypass the machine ExecutionPolicy for this local script only.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0run.ps1" %*
exit /b %ERRORLEVEL%
