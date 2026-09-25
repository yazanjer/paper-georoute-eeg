"""Upload / download assets of the GitHub release used to stage trained checkpoints before Zenodo.

  python scripts/release_assets.py upload   --release-id ID FILE [FILE ...]
  python scripts/release_assets.py download --release-id ID --out DIR [--expect N]
Token from env GITHUB_TOKEN (RunPod secret); never printed or stored.
"""
from __future__ import annotations
import argparse, hashlib, os, sys, time
import requests

REPO = os.environ.get("GEOROUTE_REPO_SLUG", "yazanjer/georoute-eeg")
API = f"https://api.github.com/repos/{REPO}"


def _h(extra=None):
    tok = os.environ.get("GITHUB_TOKEN", "").strip()
    if not tok:
        sys.exit("GITHUB_TOKEN is not set")
    h = {"Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json"}
    h.update(extra or {})
    return h


def sha256(fn):
    d = hashlib.sha256()
    with open(fn, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            d.update(b)
    return d.hexdigest()


def assets(rid):
    r = requests.get(f"{API}/releases/{rid}/assets?per_page=100", headers=_h(), timeout=60)
    r.raise_for_status()
    return r.json()


def upload(rid, files):
    have = {a["name"]: a for a in assets(rid)}
    for fn in files:
        name = os.path.basename(fn)
        if name in have:  # replace an earlier attempt
            requests.delete(f"{API}/releases/assets/{have[name]['id']}", headers=_h(), timeout=60).raise_for_status()
        with open(fn, "rb") as fh:
            r = requests.post(f"https://uploads.github.com/repos/{REPO}/releases/{rid}/assets",
                              params={"name": name, "label": f"sha256:{sha256(fn)[:16]}"},
                              headers=_h({"Content-Type": "application/zip"}), data=fh, timeout=3600)
        r.raise_for_status()
        print(f"uploaded {name} {os.path.getsize(fn)} bytes sha256 {sha256(fn)}")


def download(rid, out, expect, wait_s):
    os.makedirs(out, exist_ok=True)
    t0 = time.time()
    while True:
        al = [a for a in assets(rid) if a["name"].endswith(".zip")]
        if len(al) >= expect or time.time() - t0 > wait_s:
            break
        print(f"{len(al)}/{expect} assets present, waiting"); time.sleep(60)
    for a in al:
        fn = os.path.join(out, a["name"])
        with requests.get(a["url"], headers=_h({"Accept": "application/octet-stream"}), stream=True, timeout=3600) as r:
            r.raise_for_status()
            with open(fn, "wb") as fh:
                for b in r.iter_content(1 << 20):
                    fh.write(b)
        print(f"downloaded {a['name']} {os.path.getsize(fn)} bytes sha256 {sha256(fn)}")
    if len(al) < expect:
        sys.exit(f"only {len(al)}/{expect} assets present")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["upload", "download"])
    ap.add_argument("--release-id", required=True)
    ap.add_argument("--out", default="/workspace/zen/models")
    ap.add_argument("--expect", type=int, default=1)
    ap.add_argument("--wait-s", type=int, default=0)
    ap.add_argument("files", nargs="*")
    a = ap.parse_intermixed_args()
    upload(a.release_id, a.files) if a.cmd == "upload" else download(a.release_id, a.out, a.expect, a.wait_s)
