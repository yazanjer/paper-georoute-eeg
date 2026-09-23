#!/usr/bin/env bash
# Idempotent environment setup on the pod (keeps the image's torch/torchaudio).
set -e
MARK=/workspace/.georoute_env_ok
REQ_HASH=$(md5sum "$(dirname "$0")/../requirements.txt" | cut -d' ' -f1)
if [ -f "$MARK" ] && [ "$(cat $MARK)" = "$REQ_HASH" ]; then exit 0; fi
python - > /tmp/constraints.txt <<'PY'
import importlib.metadata as md
for p in ("torch", "torchaudio", "torchvision"):
    try:
        print(f"{p}=={md.version(p)}")
    except md.PackageNotFoundError:
        pass
PY
echo "constraints:"; cat /tmp/constraints.txt
for attempt in 1 2 3 4; do
  pip install -q --retries 10 --timeout 120 -r "$(dirname "$0")/../requirements.txt" -c /tmp/constraints.txt && break
  echo "pip attempt $attempt failed, retrying"; sleep $((attempt*20))
done
python -c "import torch, braindecode, moabb, pyriemann; print('env ok', torch.__version__, torch.cuda.is_available(), braindecode.__version__, moabb.__version__)"
echo "$REQ_HASH" > "$MARK"
