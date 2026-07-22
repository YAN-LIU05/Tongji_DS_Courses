#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

mkdir -p logs data/node1 data/node2 data/node3 data/node4 data/node5

GOEXE="${GOEXE:-go}"

for id in 1 2 3 4 5; do
  "$GOEXE" run -buildvcs=false ./cmd/node --id="$id" --config=config/cluster5.json > "logs/node${id}.log" 2>&1 &
  echo $! > "logs/node${id}.pid"
done

echo "5-node cluster started. PIDs are stored in logs/node*.pid"
