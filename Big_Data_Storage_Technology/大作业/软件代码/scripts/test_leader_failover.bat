@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0.."

set LEADER_PORT=
for %%p in (8001 8002 8003) do (
  for /f "delims=" %%l in ('powershell -NoProfile -Command "try { $s=Invoke-RestMethod -Uri http://127.0.0.1:%%p/status -TimeoutSec 1; if ($s.role -eq 'Leader') { '%%p' } } catch {}"') do set LEADER_PORT=%%l
)

if "%LEADER_PORT%"=="" (
  echo No leader found. Please start the cluster first.
  exit /b 1
)

echo Current leader API port: %LEADER_PORT%
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%LEADER_PORT%" ^| findstr "LISTENING"') do (
  echo Killing leader process PID %%a
  taskkill /PID %%a /F
)

echo Waiting for a new election...
timeout /t 3 /nobreak >nul

echo Node statuses:
curl -s http://127.0.0.1:8001/status
echo.
curl -s http://127.0.0.1:8002/status
echo.
curl -s http://127.0.0.1:8003/status
echo.

call scripts\test_basic.bat
