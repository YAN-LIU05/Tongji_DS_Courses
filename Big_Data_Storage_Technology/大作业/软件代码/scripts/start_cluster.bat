@echo off
setlocal
cd /d "%~dp0.."

if not exist logs mkdir logs
if not exist data\node1 mkdir data\node1
if not exist data\node2 mkdir data\node2
if not exist data\node3 mkdir data\node3

if "%GOEXE%"=="" set "GOEXE=D:\Go\bin\go.exe"

echo Starting Raft KV cluster...
echo Go command: %GOEXE%
start "raft-kv-node1" cmd /k ""%GOEXE%" run -buildvcs=false ./cmd/node --id=1 --config=config/cluster.json"
start "raft-kv-node2" cmd /k ""%GOEXE%" run -buildvcs=false ./cmd/node --id=2 --config=config/cluster.json"
start "raft-kv-node3" cmd /k ""%GOEXE%" run -buildvcs=false ./cmd/node --id=3 --config=config/cluster.json"

echo Done. Wait 2 seconds, then visit:
echo   http://127.0.0.1:8001/status
echo   http://127.0.0.1:8002/status
echo   http://127.0.0.1:8003/status
