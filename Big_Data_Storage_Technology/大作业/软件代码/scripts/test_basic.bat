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

echo Leader API port: %LEADER_PORT%
echo Put name=raft
curl -s -X POST http://127.0.0.1:%LEADER_PORT%/kv/put -H "Content-Type: application/json" -d "{\"key\":\"name\",\"value\":\"raft\"}"
echo.
echo Get name
curl -s http://127.0.0.1:%LEADER_PORT%/kv/get?key=name
echo.
echo Delete name
curl -s -X POST http://127.0.0.1:%LEADER_PORT%/kv/delete -H "Content-Type: application/json" -d "{\"key\":\"name\"}"
echo.
echo Get deleted name
curl -s http://127.0.0.1:%LEADER_PORT%/kv/get?key=name
echo.
