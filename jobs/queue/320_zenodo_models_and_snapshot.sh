#!/usr/bin/env bash
# Move the four seed-0 model archives from the staging GitHub release to the Zenodo DRAFT 22965131 and refresh the code
# snapshot (v1.1.0). Also regenerates the paper figures from the committed data. Never publishes.
# worker: Z
set -eo pipefail
cd "$(dirname "$0")/../.."
python -c "import requests" 2>/dev/null || pip install -q requests
mkdir -p /workspace/zen/models
python scripts/release_assets.py download --release-id 396901040 --out /workspace/zen/models --expect 4
( cd /workspace/zen/models && sha256sum *.zip ) | tee "$RESULTS_DIR/models_sha256.txt"
git archive --format=zip --prefix=georoute-eeg-v1.1.0/ -o /workspace/zen/georoute-eeg-v1.1.0.zip HEAD
cp results/201_zenodo_upload_draft/deposition.json "$RESULTS_DIR/deposition.json"
python scripts/zenodo_deposit.py delete --state "$RESULTS_DIR/deposition.json" georoute-eeg-v1.0.0.zip
python scripts/zenodo_deposit.py upload --state "$RESULTS_DIR/deposition.json" /workspace/zen/georoute-eeg-v1.1.0.zip /workspace/zen/models/*.zip
cat "$RESULTS_DIR/deposition.json"
