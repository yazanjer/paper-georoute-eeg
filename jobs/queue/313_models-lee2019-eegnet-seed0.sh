#!/usr/bin/env bash
# Export seed-0 source checkpoints of Lee2019-MI EEGNet+EA, folds 0-5 (written by job 304 to /workspace/ckpt_s0log) to the staging GitHub release for Zenodo.
# worker: S
set -eo pipefail
cd "$(dirname "$0")/../.."
python -c "import requests" 2>/dev/null || pip install -q requests
mkdir -p /workspace/zen && cd /workspace/ckpt_s0log
ls -la
sha256sum *.pt > SHA256SUMS.txt
python -c "import zipfile,glob; z=zipfile.ZipFile('/workspace/zen/models-lee2019-eegnet-seed0.zip','w',zipfile.ZIP_DEFLATED); [z.write(p) for p in sorted(glob.glob('*.pt'))+['SHA256SUMS.txt']]; z.close()"
ls -la /workspace/zen
cd - >/dev/null
cp /workspace/ckpt_s0log/SHA256SUMS.txt "$RESULTS_DIR/SHA256SUMS.txt"
python scripts/release_assets.py upload --release-id 396901040 /workspace/zen/models-lee2019-eegnet-seed0.zip | tee "$RESULTS_DIR/upload.txt"
