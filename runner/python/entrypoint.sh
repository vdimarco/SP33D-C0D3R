#!/usr/bin/env bash
set -euo pipefail
RUN_ID="$1"
cp -r /challenge /workspace/challenge
cd /workspace/challenge

echo "Ready" > /signals/status
while true; do
  if [ -f /signals/attempt ]; then
    rm -f /signals/attempt
    python /run_tests.py "$RUN_ID" || true
  fi
  sleep 0.5
done
