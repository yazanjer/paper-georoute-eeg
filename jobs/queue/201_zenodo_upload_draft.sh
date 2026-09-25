#!/usr/bin/env bash
# Upload a snapshot of this repository (code, protocol, jobs, all results) to the Zenodo DRAFT (never publishes).
# worker: Z
set -e
cd "$(dirname "$0")/../.."
python -c "import requests" 2>/dev/null || pip install -q requests
mkdir -p /workspace/zen
git archive --format=zip --prefix=georoute-eeg-v1.0.0/ -o /workspace/zen/georoute-eeg-v1.0.0.zip HEAD
ls -la /workspace/zen
cp results/200_zenodo_create_draft/deposition.json "$RESULTS_DIR/deposition.json"
python scripts/zenodo_deposit.py upload --state "$RESULTS_DIR/deposition.json" /workspace/zen/georoute-eeg-v1.0.0.zip
cat "$RESULTS_DIR/deposition.json"
