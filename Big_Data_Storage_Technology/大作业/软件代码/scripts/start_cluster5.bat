@echo off
setlocal
cd /d "%~dp0.."

if not exist logs mkdir logs
for %%i in (1 2 3 4 5) do (
  if not exist data\node%%i mkdir data\node%%i
)

if "%GOEXE%"=="" set "GOEXE=D:\Go\bin\go.exe"

echo Starting 5-node Raft KV cluster...
echo Go command: %GOEXE%
for %%i in (1 2 3 4 5) do (
  start "raft-kv-node%%i" cmd /k ""%GOEXE%" run -buildvcs=false ./cmd/node --id=%%i --config=config/cluster5.json"
)

echo Done. Wait 2 seconds, then visit:
for %%p in (8001 8002 8003 8004 8005) do (
  echo   http://127.0.0.1:%%p/status
)
