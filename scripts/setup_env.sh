#!/usr/bin/env bash
# Idempotent environment setup on the pod (keeps the image's torch).
set -e
MARK=/workspace/.georoute_env_ok
REQ_HASH=$(md5sum "$(dirname "$0")/../requirements.txt" | cut -d' ' -f1)
if [ -f "$MARK" ] && [ "$(cat $MARK)" = "$REQ_HASH" ]; then exit 0; fi
TORCH=$(python -c "import torch;print(torch.__version__.split('+')[0])")
echo "torch==$TORCH" > /tmp/constraints.txt
pip install -q -r "$(dirname "$0")/../requirements.txt" -c /tmp/constraints.txt
python -c "import torch, braindecode, moabb, pyriemann; print('env ok', torch.__version__, braindecode.__version__, moabb.__version__)"
echo "$REQ_HASH" > "$MARK"
