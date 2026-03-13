#!/usr/bin/env bash
# test_pods.sh — Full lifecycle test for `yotta pods` commands.
#
# Usage:
#   export YOTTA_API_KEY=<your-key>
#   bash scripts/test_pods.sh
#
# Optional overrides (env vars):
#   YOTTA_BASE_URL   default: https://api.yottalabs.ai
#   YOTTA_IMAGE      container image to use
#   YOTTA_GPU_TYPE   GPU type (default: NVIDIA_RTX_5090)
#   YOTTA_GPU_COUNT  GPUs (default: 1)
#   YOTTA_REGION     region(s), comma-separated (default: us-east-3)

set -euo pipefail

YOTTA="${YOTTA_CMD:-/opt/homebrew/bin/yotta}"
BASE_URL="${YOTTA_BASE_URL:-https://api.yottalabs.ai}"
IMAGE="${YOTTA_IMAGE:-nvidia/cuda:12.1.0-base-ubuntu22.04}"
GPU_TYPE="${YOTTA_GPU_TYPE:-NVIDIA_RTX_5090_32G}"
GPU_COUNT="${YOTTA_GPU_COUNT:-1}"
REGION="${YOTTA_REGION:-us-east-3}"
POD_NAME="test-pod-$(date +%s | tail -c 6)"

# ── helpers ──────────────────────────────────────────────────────────────────

log()  { echo "[$(date +%H:%M:%S)] $*"; }
pass() { echo "  ✓ $*"; }
fail() { echo "  ✗ $*" >&2; exit 1; }

run() {
    log "CMD: $*" >&2
    "$@" 2>&1
}

# Poll until the pod reaches the expected status.
# Usage: wait_for_status <pod_id> <target_status> [timeout_secs]
wait_for_status() {
    local id="$1"
    local target="$2"
    local timeout="${3:-300}"
    local elapsed=0
    local interval=10

    log "Waiting for pod $id to reach status '$target' (timeout ${timeout}s)..."
    while true; do
        local resp
        resp=$("$YOTTA" --api-key "$YOTTA_API_KEY" --base-url "$BASE_URL" pods get "$id" 2>&1)
        local status
        status=$(echo "$resp" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('data',{}).get('status','UNKNOWN'))" 2>/dev/null || echo "PARSE_ERROR")

        log "  status=$status (${elapsed}s elapsed)"

        if [[ "$status" == "$target" ]]; then
            pass "Reached '$target'"
            return 0
        fi

        if (( elapsed >= timeout )); then
            fail "Timed out waiting for '$target' (current: $status)"
        fi

        sleep "$interval"
        elapsed=$(( elapsed + interval ))
    done
}

# ── pre-flight checks ─────────────────────────────────────────────────────────

if [[ -z "${YOTTA_API_KEY:-}" ]]; then
    fail "YOTTA_API_KEY is not set. Export it before running this script."
fi

log "=== yotta pods lifecycle test ==="
log "  pod name  : $POD_NAME"
log "  image     : $IMAGE"
log "  gpu type  : $GPU_TYPE  x${GPU_COUNT}"
log "  region    : $REGION"
echo ""

# ── Step 1: List existing pods ────────────────────────────────────────────────
log "--- Step 1: List existing pods ---"
run "$YOTTA" --api-key "$YOTTA_API_KEY" --base-url "$BASE_URL" pods list
echo ""

# ── Step 2: Create pod ────────────────────────────────────────────────────────
log "--- Step 2: Create pod ---"
CREATE_RESP=$(run "$YOTTA" --api-key "$YOTTA_API_KEY" --base-url "$BASE_URL" pods create \
    --image "$IMAGE" \
    --gpu-type "$GPU_TYPE" \
    --gpu-count "$GPU_COUNT" \
    --region "$REGION" \
    --name "$POD_NAME")
echo "$CREATE_RESP"

POD_ID=$(echo "$CREATE_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('data',{}).get('id',''))" 2>/dev/null || true)

if [[ -z "$POD_ID" ]]; then
    fail "Could not parse pod ID from create response."
fi
pass "Created pod ID: $POD_ID"
echo ""

# ── Step 3: Get pod details ───────────────────────────────────────────────────
log "--- Step 3: Get pod details ---"
run "$YOTTA" --api-key "$YOTTA_API_KEY" --base-url "$BASE_URL" pods get "$POD_ID"
echo ""

# ── Step 4: Wait until RUNNING ────────────────────────────────────────────────
log "--- Step 4: Wait until RUNNING ---"
wait_for_status "$POD_ID" "RUNNING" 600
echo ""

# ── Step 5: Pause pod ─────────────────────────────────────────────────────────
log "--- Step 5: Pause pod ---"
run "$YOTTA" --api-key "$YOTTA_API_KEY" --base-url "$BASE_URL" pods pause "$POD_ID"
echo ""

# ── Step 6: Wait until PAUSED ────────────────────────────────────────────────
log "--- Step 6: Wait until PAUSED ---"
wait_for_status "$POD_ID" "PAUSED" 300
echo ""

# ── Step 7: List pods filtered by region ─────────────────────────────────────
log "--- Step 7: List pods filtered by region ---"
run "$YOTTA" --api-key "$YOTTA_API_KEY" --base-url "$BASE_URL" pods list --region "$REGION"
echo ""

# ── Step 8: Resume pod ────────────────────────────────────────────────────────
log "--- Step 8: Resume pod ---"
run "$YOTTA" --api-key "$YOTTA_API_KEY" --base-url "$BASE_URL" pods resume "$POD_ID"
echo ""

# ── Step 9: Wait until RUNNING again ─────────────────────────────────────────
log "--- Step 9: Wait until RUNNING again ---"
wait_for_status "$POD_ID" "RUNNING" 600
echo ""

# ── Step 10: Delete pod ───────────────────────────────────────────────────────
log "--- Step 10: Delete pod ---"
run "$YOTTA" --api-key "$YOTTA_API_KEY" --base-url "$BASE_URL" pods delete "$POD_ID"
echo ""

log "=== All steps completed successfully ==="
