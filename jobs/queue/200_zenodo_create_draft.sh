#!/usr/bin/env bash
# Create a Zenodo DRAFT deposition with a reserved DOI (never publishes). Token: env ZENODO_TOKEN.
# worker: Z
set -e
cd "$(dirname "$0")/../.."
python -c "import requests" 2>/dev/null || pip install -q requests
python scripts/zenodo_deposit.py create --state "$RESULTS_DIR/deposition.json"
cat "$RESULTS_DIR/deposition.json"
