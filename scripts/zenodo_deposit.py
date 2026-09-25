"""Create / fill a Zenodo draft deposition for this repository (never publishes).

Usage (token from env ZENODO_TOKEN, e.g. RunPod secret {{ RUNPOD_SECRET_zenodo }}):
  python scripts/zenodo_deposit.py create --state zenodo/deposition.json
  python scripts/zenodo_deposit.py upload --state zenodo/deposition.json FILE [FILE ...]
The state file stores only the deposition id, reserved DOI and public links - never the token.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import requests

API = os.environ.get("ZENODO_API", "https://zenodo.org/api")


def _h():
    tok = os.environ.get("ZENODO_TOKEN", "").strip()
    if not tok:
        sys.exit("ZENODO_TOKEN is not set")
    return {"Authorization": f"Bearer {tok}"}


def _check(r):
    if r.status_code >= 400:
        sys.exit(f"Zenodo error {r.status_code}: {r.text[:500]}")
    return r.json() if r.text else {}


def metadata():
    meta = json.load(open(".zenodo.json"))
    meta["prereserve_doi"] = True
    return {"metadata": meta}


def create(state):
    if os.path.exists(state):
        s = json.load(open(state))
        d = _check(requests.get(f"{API}/deposit/depositions/{s['id']}", headers=_h(), timeout=60))
        print(f"existing draft {s['id']} state={d.get('state')} doi={s.get('doi')}")
        return
    d = _check(requests.post(f"{API}/deposit/depositions", json={}, headers=_h(), timeout=60))
    d = _check(requests.put(f"{API}/deposit/depositions/{d['id']}", json=metadata(), headers=_h(), timeout=60))
    doi = (d.get("metadata", {}).get("prereserve_doi") or {}).get("doi")
    s = {"id": d["id"], "doi": doi, "state": d.get("state"),
         "html": d["links"].get("html"), "bucket": d["links"].get("bucket"), "files": []}
    os.makedirs(os.path.dirname(state) or ".", exist_ok=True)
    json.dump(s, open(state, "w"), indent=1)
    print(f"created draft {s['id']} reserved DOI {doi}")


def upload(state, files):
    s = json.load(open(state))
    d = _check(requests.get(f"{API}/deposit/depositions/{s['id']}", headers=_h(), timeout=60))
    if d.get("submitted"):
        sys.exit("deposition already published; refusing to modify")
    _check(requests.put(f"{API}/deposit/depositions/{s['id']}", json=metadata(), headers=_h(), timeout=60))
    bucket = d["links"]["bucket"]
    for fn in files:
        with open(fn, "rb") as fh:
            r = _check(requests.put(f"{bucket}/{os.path.basename(fn)}", data=fh, headers=_h(), timeout=3600))
        print(f"uploaded {fn} ({r.get('size')} bytes, {r.get('checksum')})")
    d = _check(requests.get(f"{API}/deposit/depositions/{s['id']}", headers=_h(), timeout=60))
    s["files"] = [{"name": f["filename"], "size": f["filesize"], "checksum": f["checksum"]} for f in d.get("files", [])]
    s["state"] = d.get("state")
    json.dump(s, open(state, "w"), indent=1)
    print(f"draft {s['id']} now has {len(s['files'])} files; NOT published")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["create", "upload"])
    ap.add_argument("--state", default="zenodo/deposition.json")
    ap.add_argument("files", nargs="*")
    a = ap.parse_intermixed_args()
    create(a.state) if a.cmd == "create" else upload(a.state, a.files)
