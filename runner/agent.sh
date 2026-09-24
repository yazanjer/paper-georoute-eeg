#!/usr/bin/env bash
# GeoRoute pod agent: pull repo, run queued jobs, push results back.
# Requires env GITHUB_TOKEN (set from RunPod secret {{ RUNPOD_SECRET_github_token }}).
#  - single instance (flock)
#  - jobs run in background; a live log tail is pushed every PROGRESS seconds
#  - touch jobs/STOP in the repo to pause picking new jobs
set -u
exec 9>/workspace/agent.lock
if ! flock -n 9; then echo "[agent] another agent holds the lock, exiting"; exit 0; fi

REPO="${GEOROUTE_REPO:-yazanjer/georoute-eeg}"
WORK="${GEOROUTE_WORK:-/workspace/georoute-eeg}"
POLL="${GEOROUTE_POLL:-60}"
PROGRESS="${GEOROUTE_PROGRESS:-300}"
URL="https://x-access-token:${GITHUB_TOKEN}@github.com/${REPO}.git"

git config --global user.name  "georoute-runpod-agent"
git config --global user.email "georoute-runpod-agent@users.noreply.github.com"
git config --global pull.rebase true
git config --global rebase.autoStash true

[ -d "$WORK/.git" ] || git clone "$URL" "$WORK"
cd "$WORK"
git remote set-url origin "$URL"

push() {  # commit + push with retry
  git add -A results status 2>/dev/null
  git commit -qm "$1" || return 0
  for i in 1 2 3 4 5 6; do
    git pull -q --rebase -X theirs && git push -q && return 0
    sleep $((i*5))
  done
  echo "[agent] push failed: $1"
}

heartbeat() {
  mkdir -p status
  local gpu
  gpu=$(nvidia-smi --query-gpu=name,memory.used,memory.total,utilization.gpu --format=csv,noheader 2>/dev/null | head -1)
  printf '{"time": "%s", "pod": "%s", "gpu": "%s", "state": "%s", "agent_pid": %s}\n' \
    "$(date -u +%FT%TZ)" "${RUNPOD_POD_ID:-unknown}" "$gpu" "$1" "$$" > "status/pod_${GEOROUTE_WORKER:-default}.json"
  tail -n 60 /workspace/agent.log > "status/agent_log_tail_${GEOROUTE_WORKER:-default}.txt" 2>/dev/null || true
}

LAST_HB=0
while true; do
  git pull -q --rebase || echo "[agent] pull failed"
  ran=0
  if [ ! -f jobs/STOP ]; then
    for job in jobs/queue/*.sh; do
      [ -e "$job" ] || continue
      name=$(basename "$job" .sh)
      out="results/$name"
      [ -f "$out/status" ] && continue
      want=$(grep -m1 '^# worker:' "$job" | awk '{print $3}')
      if [ -n "$want" ] && [ "$want" != "${GEOROUTE_WORKER:-}" ]; then continue; fi
      mkdir -p "$out"
      echo running > "$out/status"; git rev-parse HEAD > "$out/commit"; date -u +%FT%TZ > "$out/started"
      heartbeat "running $name"; push "start $name"
      log="/workspace/logs_$name.txt"
      RESULTS_DIR="$WORK/$out" bash "$job" > "$log" 2>&1 &
      pid=$!
      t_last=$(date +%s)
      while kill -0 $pid 2>/dev/null; do
        sleep 20
        if [ $(( $(date +%s) - t_last )) -ge "$PROGRESS" ]; then
          tail -n 150 "$log" > "$out/log_live.txt"
          heartbeat "running $name"; push "progress $name"
          t_last=$(date +%s)
        fi
      done
      wait $pid; code=$?
      tail -n 300 "$log" > "$out/log_tail.txt"; rm -f "$out/log_live.txt"
      echo $code > "$out/exit_code"; date -u +%FT%TZ > "$out/finished"
      [ $code -eq 0 ] && echo done > "$out/status" || echo failed > "$out/status"
      heartbeat "idle"; push "finish $name (exit $code)"
      ran=1
      break   # re-pull after every job so new code is picked up
    done
  fi
  if [ $ran -eq 0 ]; then
    if [ $(( $(date +%s) - LAST_HB )) -ge 600 ]; then
      heartbeat "idle"; push "heartbeat"; LAST_HB=$(date +%s)
    fi
    sleep "$POLL"
  fi
done
