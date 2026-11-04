"""Audit: target labels are used only for scoring.

Runs the full TTA pipeline twice on the same target stream, once with the true scored-session labels and once
with those labels randomly permuted, and checks that every method's per-trial predictions are IDENTICAL
(only the accuracies may differ). Any use of target labels during adaptation or prediction would break this.

usage: python scripts/check_label_isolation.py [--synthetic 1] [--dataset bnci2014_001 --backbone eegnet ...]
Extra arguments are passed to run_tta.py; runs on CPU so the two passes are bit-for-bit deterministic.
"""
import glob, json, os, subprocess, sys, tempfile

here = os.path.dirname(os.path.abspath(__file__))
extra = sys.argv[1:] or ["--synthetic", "1", "--epochs", "2", "--cv", "loso", "--fold-ids", "0",
                         "--backbone", "eegnet", "--bs", "8", "--warmup", "16"]
methods = "source,t3a,lame,tent,tent@1e-4,shot_im,shot_im@1e-5,shot_past,rctta,rctta+t3a,rctta_offline,geo_src"
tmp = tempfile.mkdtemp()
env = dict(os.environ, CUDA_VISIBLE_DEVICES="", PYTHONHASHSEED="0")   # CPU: bit-for-bit deterministic
outs = []
for perm in (0, 1):
    out = os.path.join(tmp, f"perm{perm}")
    cmd = [sys.executable, os.path.join(here, "run_tta.py"), *extra, "--methods", methods, "--save-preds", "1",
           "--permute-scored-labels", str(perm), "--ckpt-dir", os.path.join(tmp, "ckpt"), "--out", out]
    subprocess.run(cmd, check=True, env=env)
    outs.append({os.path.basename(f): json.load(open(f)) for f in glob.glob(os.path.join(out, "*.json"))})
ok, report = True, {}
for fn, r0 in outs[0].items():
    r1 = outs[1][fn]
    same_labels = r0["y_stream"] == r1["y_stream"]
    for m, p0 in r0["preds"].items():
        p1 = r1["preds"][m]
        n_diff = sum(a != b for a, b in zip(p0, p1))
        report[f"{fn}:{m}"] = {"pred_differences": n_diff, "acc_true": r0["methods"][m]["acc"], "acc_permuted": r1["methods"][m]["acc"]}
        ok &= n_diff == 0
    report[f"{fn}:labels_were_permuted"] = not same_labels
print(json.dumps(report, indent=1))
print("LABEL ISOLATION:", "PASSED (identical predictions with permuted target labels)" if ok else "FAILED")
sys.exit(0 if ok else 1)
