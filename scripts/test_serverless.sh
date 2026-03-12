#!/usr/bin/env bash
# test_serverless.sh — Full lifecycle test for `yotta serverless` commands.
#
# Usage:
#   export YOTTA_API_KEY=<your-key>
#   bash scripts/test_serverless.sh
#
# Optional overrides (env vars):
#   YOTTA_BASE_URL   default: https://api.yottalabs.ai
#   YOTTA_IMAGE      container image to use
#   YOTTA_REGION     resource region
#   YOTTA_GPU_TYPE   GPU type
#   YOTTA_GPU_COUNT  GPUs per worker
#   YOTTA_WORKERS    initial workers
#   YOTTA_VOLUME     container volume in GB (min 20)
#   YOTTA_SVC_MODE   service mode: ALB | QUEUE | CUSTOM (default: QUEUE)

set -euo pipefail

YOTTA="${YOTTA_CMD:-/opt/homebrew/bin/yotta}"
BASE_URL="${YOTTA_BASE_URL:-https://api.yottalabs.ai}"
IMAGE="${YOTTA_IMAGE:-yottalabsai/pytorch:2.8.0-py3.11-cuda12.8.1-cudnn-devel-ubuntu22.04-2025081902}"
REGION="${YOTTA_REGION:-us-east}"
GPU_TYPE="${YOTTA_GPU_TYPE:-NVIDIA_RTX_5090_32G}"
GPU_COUNT="${YOTTA_GPU_COUNT:-1}"
WORKERS="${YOTTA_WORKERS:-1}"
VOLUME="${YOTTA_VOLUME:-256}"
SVC_MODE="${YOTTA_SVC_MODE:-QUEUE}"
ENDPOINT_NAME="test-$(date +%s | tail -c 7)"   # ≤20 chars

RESOURCES='[{"region":"'"$REGION"'","gpuType":"'"$GPU_TYPE"'","gpuCount":'"$GPU_COUNT"'}]'

# ── helpers ──────────────────────────────────────────────────────────────────

log()  { echo "[$(date +%H:%M:%S)] $*"; }
pass() { echo "  ✓ $*"; }
fail() { echo "  ✗ $*" >&2; exit 1; }

run() {
    log "CMD: $*" >&2
    "$@" 2>&1
}

# Like run(), but fails if the response JSON has code != 10000.
run_ok() {
    local resp
    resp=$(run "$@")
    echo "$resp"
    local code
    code=$(echo "$resp" | python3 -c "import sys,json; print(json.load(sys.stdin).get('code',''))" 2>/dev/null || echo "")
    if [[ "$code" != "10000" ]]; then
        fail "API returned non-success code: $code"
    fi
}

# Poll until the deployment reaches the expected status.
# Usage: wait_for_status <deployment_id> <target_status> [timeout_secs]
wait_for_status() {
    local id="$1"
    local target="$2"
    local timeout="${3:-300}"
    local elapsed=0
    local interval=10

    log "Waiting for deployment $id to reach status '$target' (timeout ${timeout}s)..."
    while true; do
        local resp
        resp=$("$YOTTA" --api-key "$YOTTA_API_KEY" --base-url "$BASE_URL" serverless get "$id" 2>&1)
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

log "=== yotta serverless lifecycle test ==="
log "  endpoint name : $ENDPOINT_NAME"
log "  image         : $IMAGE"
log "  resources     : $RESOURCES"
log "  workers       : $WORKERS"
log "  service mode  : $SVC_MODE"
log "  volume        : ${VOLUME}GB"
echo ""

# ── Step 1: List existing deployments ─────────────────────────────────────────
log "--- Step 1: List existing deployments ---"
run "$YOTTA" --api-key "$YOTTA_API_KEY" --base-url "$BASE_URL" serverless list
echo ""

# ── Step 2: Create deployment ──────────────────────────────────────────────────
log "--- Step 2: Create deployment ---"
CREATE_RESP=$(run_ok "$YOTTA" --api-key "$YOTTA_API_KEY" --base-url "$BASE_URL" serverless create \
    --name "$ENDPOINT_NAME" \
    --image "$IMAGE" \
    --resources "$RESOURCES" \
    --workers "$WORKERS" \
    --service-mode "$SVC_MODE" \
    --volume "$VOLUME")
echo "$CREATE_RESP"

DEPLOY_ID=$(echo "$CREATE_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('data',{}).get('id',''))" 2>/dev/null || true)

if [[ -z "$DEPLOY_ID" ]]; then
    fail "Could not parse deployment ID from create response."
fi
pass "Created deployment ID: $DEPLOY_ID"
echo ""

# ── Step 3: Get deployment details ────────────────────────────────────────────
log "--- Step 3: Get deployment details ---"
run "$YOTTA" --api-key "$YOTTA_API_KEY" --base-url "$BASE_URL" serverless get "$DEPLOY_ID"
echo ""

# ── Step 4: Wait until RUNNING ────────────────────────────────────────────────
log "--- Step 4: Wait until RUNNING ---"
wait_for_status "$DEPLOY_ID" "RUNNING" 600
echo ""

# ── Step 5: List workers ──────────────────────────────────────────────────────
log "--- Step 5: List workers ---"
run "$YOTTA" --api-key "$YOTTA_API_KEY" --base-url "$BASE_URL" serverless workers "$DEPLOY_ID"
echo ""

# ── Step 6: Scale workers (increase by 1) ─────────────────────────────────────
NEW_WORKERS=$(( WORKERS + 1 ))
log "--- Step 6: Scale to $NEW_WORKERS workers ---"
run "$YOTTA" --api-key "$YOTTA_API_KEY" --base-url "$BASE_URL" serverless scale "$DEPLOY_ID" --workers "$NEW_WORKERS"
echo ""

# ── Step 7: Stop deployment ───────────────────────────────────────────────────
log "--- Step 7: Stop deployment ---"
run "$YOTTA" --api-key "$YOTTA_API_KEY" --base-url "$BASE_URL" serverless stop "$DEPLOY_ID"
echo ""

# ── Step 8: Wait until STOPPED ────────────────────────────────────────────────
log "--- Step 8: Wait until STOPPED ---"
wait_for_status "$DEPLOY_ID" "STOPPED" 300
echo ""

# ── Step 9: List with status filter ───────────────────────────────────────────
log "--- Step 9: List deployments filtered by STOPPED ---"
run "$YOTTA" --api-key "$YOTTA_API_KEY" --base-url "$BASE_URL" serverless list --status STOPPED
echo ""

# ── Step 10: Start deployment ─────────────────────────────────────────────────
log "--- Step 10: Start deployment ---"
run "$YOTTA" --api-key "$YOTTA_API_KEY" --base-url "$BASE_URL" serverless start "$DEPLOY_ID"
echo ""

# ── Step 11: Wait until RUNNING again ─────────────────────────────────────────
log "--- Step 11: Wait until RUNNING again ---"
wait_for_status "$DEPLOY_ID" "RUNNING" 600
echo ""

# ── Step 12: Stop before delete ───────────────────────────────────────────────
log "--- Step 12: Stop before delete ---"
run_ok "$YOTTA" --api-key "$YOTTA_API_KEY" --base-url "$BASE_URL" serverless stop "$DEPLOY_ID"
echo ""

# ── Step 13: Wait until STOPPED ───────────────────────────────────────────────
log "--- Step 13: Wait until STOPPED ---"
wait_for_status "$DEPLOY_ID" "STOPPED" 300
echo ""

# ── Step 14: Delete deployment ────────────────────────────────────────────────
log "--- Step 14: Delete deployment ---"
run_ok "$YOTTA" --api-key "$YOTTA_API_KEY" --base-url "$BASE_URL" serverless delete "$DEPLOY_ID"
echo ""

log "=== All steps completed successfully ==="
