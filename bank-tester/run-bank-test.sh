#!/usr/bin/env bash
#
# Bank Tester: run the tester Claude against a fresh UniFi controller using the MCP server.
#
# Usage (from repo root):
#   bash bank-tester/run-bank-test.sh [task-filter]
#
# Examples:
#   bash bank-tester/run-bank-test.sh              # run all tasks
#   bash bank-tester/run-bank-test.sh 01            # run only task 01
#   bash bank-tester/run-bank-test.sh "01 03 05"    # run tasks 01, 03, 05
#   MODEL=opus bash bank-tester/run-bank-test.sh    # use Opus model
#
# Requires: docker, claude CLI on PATH, fastmcp on PATH
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_DIR"

# --- Docker socket (NixOS default context often points to podman socket) ---
export DOCKER_HOST="unix:///var/run/docker.sock"

# --- Logging helpers ---
ts() { date '+%H:%M:%S'; }
log() { echo "[$(ts)] $*"; }
logf() { echo "[$(ts)] $*" | tee -a "$LIVE_LOG"; }

CONTAINER="unifi-test-controller"
USERNAME="admin"
PASSWORD="testpassword123"
HTTPS_PORT=8443
INFORM_PORT=8080
MCP_CONFIG_TEMPLATE="bank-tester/mcp-config.json"
TESTER_PROMPT="bank-tester/TESTER-CLAUDE.md"
TASKS_DIR="bank-tester/tasks"
TASK_FILTER="${1:-}"
MODEL="${MODEL:-sonnet}"

# --- Preflight checks ---
[[ -f "$MCP_CONFIG_TEMPLATE" ]] || { log "FATAL: $MCP_CONFIG_TEMPLATE not found."; exit 1; }
[[ -f "$TESTER_PROMPT" ]] || { log "FATAL: $TESTER_PROMPT not found."; exit 1; }
[[ -d "$TASKS_DIR" ]] || { log "FATAL: $TASKS_DIR not found. Run generate-tasks.py first."; exit 1; }
command -v claude >/dev/null 2>&1 || { log "FATAL: claude CLI not found on PATH."; exit 1; }
command -v docker >/dev/null 2>&1 || { log "FATAL: docker not found on PATH."; exit 1; }

# Resolve fastmcp to absolute path
FASTMCP_PATH="$(command -v fastmcp 2>/dev/null || true)"
if [[ -z "$FASTMCP_PATH" ]]; then
    # Try uv run path
    FASTMCP_PATH="$(uv run which fastmcp 2>/dev/null || true)"
    if [[ -z "$FASTMCP_PATH" ]]; then
        log "FATAL: fastmcp not found on PATH."
        exit 1
    fi
fi
log "Using fastmcp: $FASTMCP_PATH"
log "Using model: $MODEL"

# --- Create results directory ---
RUN_ID="$(date +%Y%m%d-%H%M%S)"
RESULTS_DIR="bank-tester/results/run-${RUN_ID}"
mkdir -p "$RESULTS_DIR"
log "Results dir: $RESULTS_DIR"

# --- Create live log early (logf needs it) ---
LIVE_LOG="${RESULTS_DIR}/live.log"
touch "$LIVE_LOG"

# --- Cleanup on exit ---
cleanup() {
    log "Cleaning up..."
    docker compose -f docker-compose.test.yml down -v 2>/dev/null || true
    rm -f "${RESULTS_DIR}/mcp-config-live.json"
    log "Done."
}
trap cleanup EXIT

# --- Start UniFi controller ---
log "Starting UniFi controller..."
docker compose -f docker-compose.test.yml up -d

log "Waiting for container to become healthy..."
MAX_WAIT=180
WAITED=0
while [[ $WAITED -lt $MAX_WAIT ]]; do
    if docker compose -f docker-compose.test.yml ps --format json 2>/dev/null | grep -q '"healthy"'; then
        echo ""
        log "Container is healthy! (${WAITED}s)"
        break
    fi
    if (( WAITED % 10 == 0 && WAITED > 0 )); then
        echo -n " [${WAITED}s]"
    else
        echo -n "."
    fi
    sleep 5
    WAITED=$((WAITED + 5))
done

if [[ $WAITED -ge $MAX_WAIT ]]; then
    echo ""
    log "FATAL: Controller not healthy after ${MAX_WAIT}s"
    docker compose -f docker-compose.test.yml logs --tail=50
    exit 1
fi

# --- Seed admin via MongoDB ---
log "Seeding admin user via MongoDB..."

# Wait for MongoDB
for i in $(seq 1 60); do
    if docker exec "$CONTAINER" mongo --port 27117 --quiet --eval "db.runCommand({ping:1})" ace >/dev/null 2>&1; then
        MONGO_CMD="mongo"
        log "MongoDB ready (mongo shell)"
        break
    fi
    if docker exec "$CONTAINER" mongosh --port 27117 --quiet --eval "db.runCommand({ping:1})" ace >/dev/null 2>&1; then
        MONGO_CMD="mongosh"
        log "MongoDB ready (mongosh shell)"
        break
    fi
    if [[ $i -eq 60 ]]; then
        log "FATAL: MongoDB did not become ready"
        exit 1
    fi
    sleep 2
done

# Generate password hash
HASH=$(docker exec "$CONTAINER" openssl passwd -6 "$PASSWORD" 2>/dev/null || \
       python3 -c "import crypt; print(crypt.crypt('$PASSWORD', crypt.mksalt(crypt.METHOD_SHA512)))")

# Insert admin + grant privileges
docker exec "$CONTAINER" $MONGO_CMD --port 27117 --quiet ace --eval "
var existing = db.admin.findOne({name: '$USERNAME'});
if (!existing) {
    db.admin.insert({
        email: 'admin@test.local',
        last_site_name: 'default',
        name: '$USERNAME',
        x_shadow: '$HASH'
    });
    var admin = db.admin.findOne({name: '$USERNAME'});
    var adminId = admin._id.toString();
    var sites = db.site.find().toArray();
    sites.forEach(function(site) {
        db.privilege.insert({
            admin_id: adminId,
            site_id: site._id.toString(),
            role: 'admin',
            permissions: []
        });
        print('  Granted admin for site: ' + site.name);
    });
    print('  Admin created: ' + adminId);
} else {
    print('  Admin already exists');
}
"

# --- Wait for login to work ---
log "Waiting for login API..."
for i in $(seq 1 30); do
    HTTP_CODE=$(curl -sk -o /dev/null -w "%{http_code}" \
        -X POST "https://127.0.0.1:${HTTPS_PORT}/api/login" \
        -H "Content-Type: application/json" \
        -d "{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\"}" 2>/dev/null || echo "000")
    if [[ "$HTTP_CODE" == "200" ]]; then
        log "Login works! (HTTP 200)"
        break
    fi
    if [[ $i -eq 30 ]]; then
        log "FATAL: Login still failing after 60s (HTTP $HTTP_CODE)"
        exit 1
    fi
    sleep 2
done

# --- Wait for API to be fully ready (avoid startup race) ---
log "Waiting for API to fully initialize..."
for i in $(seq 1 15); do
    SELF_CHECK=$(curl -sk -o /dev/null -w "%{http_code}" \
        -b /tmp/unifi_test_cookies.txt \
        "https://127.0.0.1:${HTTPS_PORT}/api/self" 2>/dev/null || echo "000")
    # First do a login to get cookies
    if [[ $i -eq 1 ]]; then
        curl -sk -c /tmp/unifi_test_cookies.txt -o /dev/null \
            -X POST "https://127.0.0.1:${HTTPS_PORT}/api/login" \
            -H "Content-Type: application/json" \
            -d "{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\"}" 2>/dev/null || true
    fi
    SELF_CHECK=$(curl -sk -o /dev/null -w "%{http_code}" \
        -b /tmp/unifi_test_cookies.txt \
        "https://127.0.0.1:${HTTPS_PORT}/api/self" 2>/dev/null || echo "000")
    if [[ "$SELF_CHECK" == "200" ]]; then
        log "API fully ready (/api/self returns 200)"
        rm -f /tmp/unifi_test_cookies.txt
        break
    fi
    if [[ $i -eq 15 ]]; then
        log "WARNING: /api/self still not returning 200 after 30s, proceeding anyway"
        rm -f /tmp/unifi_test_cookies.txt
    fi
    sleep 2
done

# --- Build live MCP config ---
LIVE_MCP_CONFIG="${RESULTS_DIR}/mcp-config-live.json"
sed -e "s|FASTMCP_PATH_PLACEHOLDER|${FASTMCP_PATH}|g" \
    -e "s|REPO_DIR_PLACEHOLDER|${REPO_DIR}|g" \
    -e "s|ADMIN_PASS_PLACEHOLDER|${PASSWORD}|g" \
    "$MCP_CONFIG_TEMPLATE" > "$LIVE_MCP_CONFIG"
log "MCP config: $LIVE_MCP_CONFIG"

# --- Quick MCP server smoke test ---
log "Smoke-testing MCP server..."
MCP_SMOKE=$(timeout 10 "$FASTMCP_PATH" run "$REPO_DIR/generated/server.py" --transport stdio <<< '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"smoke","version":"0.1"}}}' 2>/dev/null | head -1 || true)
if [[ -n "$MCP_SMOKE" ]] && echo "$MCP_SMOKE" | python3 -c "import sys,json; d=json.load(sys.stdin); assert 'result' in d" 2>/dev/null; then
    log "MCP server responds OK"
else
    log "WARNING: MCP server smoke test inconclusive (may still work via claude CLI)"
fi

# --- Collect task files ---
TASK_FILES=()
for task_file in "$TASKS_DIR"/*.md; do
    task_basename="$(basename "$task_file" .md)"

    if [[ -n "$TASK_FILTER" ]]; then
        match=false
        for pattern in $TASK_FILTER; do
            if [[ "$task_basename" == *"$pattern"* ]]; then
                match=true
                break
            fi
        done
        if [[ "$match" == "false" ]]; then
            continue
        fi
    fi
    TASK_FILES+=("$task_file")
done

if [[ ${#TASK_FILES[@]} -eq 0 ]]; then
    log "FATAL: No task files found matching filter '${TASK_FILTER}'"
    exit 1
fi

log "Running ${#TASK_FILES[@]} task(s)..."
log "Tail the live log: tail -f ${LIVE_LOG}"
echo ""

# --- Run each task ---
PASSED=0
FAILED=0
TASK_NUM=0
TESTER_SYSTEM_PROMPT="$(cat "$TESTER_PROMPT")"

for task_file in "${TASK_FILES[@]}"; do
    task_name="$(basename "$task_file" .md)"
    TASK_NUM=$((TASK_NUM + 1))
    logf "=== Task ${TASK_NUM}/${#TASK_FILES[@]}: $task_name ==="
    task_content="$(cat "$task_file")"

    # Log the claude CLI invocation
    CLAUDE_CMD="claude -p --mcp-config $LIVE_MCP_CONFIG --strict-mcp-config --permission-mode bypassPermissions --output-format text --model $MODEL --max-budget-usd 200.00"
    logf "  cmd: $CLAUDE_CMD"
    logf "  task file: $task_file ($(wc -c < "$task_file") bytes)"

    # Quick API health check
    API_CHECK=$(curl -sk -m 5 -o /dev/null -w '%{http_code}' \
        -X POST "https://127.0.0.1:${HTTPS_PORT}/api/login" \
        -H "Content-Type: application/json" \
        -d "{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\"}" 2>/dev/null || echo "000")
    if [[ "$API_CHECK" != "200" ]]; then
        logf "  WARNING: API returned $API_CHECK before task start"
    fi

    TASK_START=$(date +%s)

    # Run tester Claude with text output
    set +e
    claude -p \
        --mcp-config "$LIVE_MCP_CONFIG" \
        --strict-mcp-config \
        --permission-mode bypassPermissions \
        --output-format text \
        --model "$MODEL" \
        --max-budget-usd 200.00 \
        --append-system-prompt "$TESTER_SYSTEM_PROMPT" \
        "$task_content" \
        2> "${RESULTS_DIR}/${task_name}.stderr" \
        | tee "${RESULTS_DIR}/${task_name}.txt" >> "$LIVE_LOG"
    task_exit=${PIPESTATUS[0]}
    set -e

    TASK_END=$(date +%s)
    TASK_DURATION=$((TASK_END - TASK_START))
    OUTPUT_SIZE=$(wc -c < "${RESULTS_DIR}/${task_name}.txt")
    STDERR_SIZE=$(wc -c < "${RESULTS_DIR}/${task_name}.stderr" 2>/dev/null || echo 0)

    if [[ $task_exit -eq 0 ]]; then
        logf "  PASS (exit $task_exit, ${TASK_DURATION}s, output=${OUTPUT_SIZE}B, stderr=${STDERR_SIZE}B)"
        PASSED=$((PASSED + 1))
    else
        logf "  FAIL (exit $task_exit, ${TASK_DURATION}s, output=${OUTPUT_SIZE}B, stderr=${STDERR_SIZE}B)"
        FAILED=$((FAILED + 1))
    fi

    # Always show stderr if non-empty
    if [[ -s "${RESULTS_DIR}/${task_name}.stderr" ]]; then
        logf "  --- stderr (first 10 lines) ---"
        head -10 "${RESULTS_DIR}/${task_name}.stderr" | sed 's/^/  | /' | tee -a "$LIVE_LOG"
        logf "  --- end stderr ---"
    fi

    # Warn if output is suspiciously small
    if [[ $OUTPUT_SIZE -lt 50 ]]; then
        logf "  WARNING: Output is only ${OUTPUT_SIZE} bytes — Claude may not have called any tools"
    fi

    echo "" | tee -a "$LIVE_LOG"
done

# --- Analyze results ---
log "Analyzing results..."
python3 bank-tester/analyze-results.py "$RESULTS_DIR"

echo ""
log "=== Bank Test Complete ==="
log "  Passed: $PASSED / ${#TASK_FILES[@]}"
log "  Failed: $FAILED / ${#TASK_FILES[@]}"
log "  Results: $RESULTS_DIR"
log "  Summary: ${RESULTS_DIR}/summary.md"

exit $FAILED
