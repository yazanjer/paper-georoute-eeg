# GeoRoute-EEG

**GeoRoute: Label-Free Riemannian Routing of Subject-Specific LoRA Adapters for Calibration-Free EEG Foundation Model Decoding**

Code, experiment jobs and results for the GeoRoute study. Experiments run on RunPod GPU pods; code and results are archived on Zenodo through its GitHub integration: each GitHub release gets a DOI.

## Layout

```
runner/agent.sh     pod-side loop: git pull -> run queued jobs -> push results
jobs/queue/*.sh     experiment jobs (one file = one job)
results/<job>/      status, exit code, log tail, metrics (json/csv) pushed back by the pod
src/                method + baselines (to be added)
.zenodo.json        Zenodo archive metadata
```

## How execution works

1. A RunPod pod starts from the `georoute-agent` template. Its start command clones this repo using the RunPod secret `github_token` and runs `runner/agent.sh`.
2. The agent polls `main` every 60 s. Any `jobs/queue/<name>.sh` without `results/<name>/status` is run.
3. The agent writes `results/<name>/{status,exit_code,log_tail.txt}` plus any metrics the job saves into `$RESULTS_DIR`, then commits and pushes.
4. Large artifacts (checkpoints, raw data) stay on the pod volume `/workspace`; only small result files are committed.

## Reproducibility

Every result is tied to the git commit that produced it (`results/<job>/commit`).
