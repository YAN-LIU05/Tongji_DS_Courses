#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

leader_port=""
for port in 8001 8002 8003; do
  role="$(curl -fs "http://127.0.0.1:${port}/status" | sed -n 's/.*"role":"\([^"]*\)".*/\1/p' || true)"
  if [ "$role" = "Leader" ]; then
    leader_port="$port"
  fi
done

if [ -z "$leader_port" ]; then
  echo "No leader found. Please start the cluster first."
  exit 1
fi

echo "Leader API port: ${leader_port}"
curl -s -X POST "http://127.0.0.1:${leader_port}/kv/put" -H "Content-Type: application/json" -d '{"key":"name","value":"raft"}'
echo
curl -s "http://127.0.0.1:${leader_port}/kv/get?key=name"
echo
curl -s -X POST "http://127.0.0.1:${leader_port}/kv/delete" -H "Content-Type: application/json" -d '{"key":"name"}'
echo
curl -s "http://127.0.0.1:${leader_port}/kv/get?key=name"
echo
