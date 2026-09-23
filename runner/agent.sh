#!/usr/bin/env bash
# GeoRoute pod agent: pull repo, run queued jobs, push results back.
# Requires env GITHUB_TOKEN (set from RunPod secret {{ RUNPOD_SECRET_github_token }}).
set -u
REPO="${GEOROUTE_REPO:-yazanjer/georoute-eeg}"
WORK="${GEOROUTE_WORK:-/workspace/georoute-eeg}"
POLL="${GEOROUTE_POLL:-60}"
URL="https://x-access-token:${GITHUB_TOKEN}@github.com/${REPO}.git"

git config --global user.name  "georoute-runpod-agent"
git config --global user.email "georoute-runpod-agent@users.noreply.github.com"
git config --global pull.rebase true

[ -d "$WORK/.git" ] || git clone "$URL" "$WORK"
cd "$WORK"
git remote set-url origin "$URL"

push() {  # commit + push with retry
  git add -A results status 2>/dev/null
  git commit -qm "$1" || return 0
  for i in 1 2 3 4 5; do
    git pull -q --rebase -X theirs && git push -q && return 0
    sleep $((i*5))
  done
  echo "[agent] push failed: $1"
}

heartbeat() {
  mkdir -p status
  {
    echo "{\"time\": \"$(date -u +%FT%TZ)\", \"pod\": \"${RUNPOD_POD_ID:-unknown}\", \"gpu\": \"$(nvidia-smi --query-gpu=name,memory.used,memory.total,utilization.gpu --format=csv,noheader 2>/dev/null | head -1)\", \"state\": \"$1\"}"
  } > status/pod.json
}

while true; do
  git pull -q --rebase || true
  ran=0
  for job in jobs/queue/*.sh; do
    [ -e "$job" ] || continue
    name=$(basename "$job" .sh)
    out="results/$name"
    [ -f "$out/status" ] && continue
    mkdir -p "$out"
    echo running > "$out/status"; git rev-parse HEAD > "$out/commit"; date -u +%FT%TZ > "$out/started"
    heartbeat "running $name"; push "start $name"
    RESULTS_DIR="$WORK/$out" bash "$job" > "/workspace/logs_$name.txt" 2>&1
    code=$?
    tail -n 300 "/workspace/logs_$name.txt" > "$out/log_tail.txt"
    echo $code > "$out/exit_code"; date -u +%FT%TZ > "$out/finished"
    [ $code -eq 0 ] && echo done > "$out/status" || echo failed > "$out/status"
    heartbeat "idle"; push "finish $name (exit $code)"
    ran=1
    break   # re-pull after every job so new code is picked up
  done
  if [ $ran -eq 0 ]; then
    heartbeat "idle"
    # heartbeat push at most every 10 min
    if [ $(( $(date +%s) / 600 )) -ne "${LAST_HB:-0}" ]; then LAST_HB=$(( $(date +%s) / 600 )); push "heartbeat"; fi
    sleep "$POLL"
  fi
done
