#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

mkdir -p logs data/node1 data/node2 data/node3

GOEXE="${GOEXE:-go}"

"$GOEXE" run -buildvcs=false ./cmd/node --id=1 --config=config/cluster.json > logs/node1.log 2>&1 &
echo $! > logs/node1.pid
"$GOEXE" run -buildvcs=false ./cmd/node --id=2 --config=config/cluster.json > logs/node2.log 2>&1 &
echo $! > logs/node2.pid
"$GOEXE" run -buildvcs=false ./cmd/node --id=3 --config=config/cluster.json > logs/node3.log 2>&1 &
echo $! > logs/node3.pid

echo "Cluster started. PIDs are stored in logs/node*.pid"
