#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

for pid_file in logs/node*.pid; do
  [ -e "$pid_file" ] || continue
  pid="$(cat "$pid_file")"
  if kill -0 "$pid" 2>/dev/null; then
    kill "$pid"
  fi
  rm -f "$pid_file"
done

echo "Cluster stopped."
