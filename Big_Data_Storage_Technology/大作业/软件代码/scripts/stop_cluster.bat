@echo off
setlocal
echo Stopping processes listening on Raft KV ports...

for %%p in (8001 8002 8003 8004 8005 9001 9002 9003 9004 9005) do (
  for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%%p" ^| findstr "LISTENING"') do (
    echo Killing PID %%a on port %%p
    taskkill /PID %%a /F >nul 2>nul
  )
)

echo Done.
