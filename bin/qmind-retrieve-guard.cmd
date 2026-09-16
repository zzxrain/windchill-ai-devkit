@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0qmind-retrieve-guard.ps1"
exit /b %ERRORLEVEL%