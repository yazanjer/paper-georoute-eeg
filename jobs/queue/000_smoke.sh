#!/usr/bin/env bash
# Smoke test: GPU, torch, install core EEG stack, check a MOABB dataset download.
set -e
nvidia-smi
python -c "import torch;print('torch',torch.__version__,'cuda',torch.cuda.is_available(),torch.cuda.get_device_name(0) if torch.cuda.is_available() else '')"
pip install -q moabb braindecode pyriemann peft mne scikit-learn pandas 2>&1 | tail -5
python - <<'EOF'
import json, os, torch, moabb, braindecode, pyriemann, mne
info = dict(torch=torch.__version__, cuda=torch.cuda.is_available(),
            gpu=torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
            moabb=moabb.__version__, braindecode=braindecode.__version__,
            pyriemann=pyriemann.__version__, mne=mne.__version__)
from moabb.datasets import BNCI2014_001
ds = BNCI2014_001()
data = ds.get_data(subjects=[1])
info['bnci2014_001_subject1_sessions'] = list(data[1].keys())
print(info)
json.dump(info, open(os.path.join(os.environ['RESULTS_DIR'], 'env.json'), 'w'), indent=2)
EOF
