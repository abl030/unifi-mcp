#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

CONTAINER="unifi-test-controller"
USERNAME="admin"
PASSWORD="testpassword123"
PORT="8443"

cleanup() {
    echo ""
    echo "=== Cleanup: tearing down containers ==="
    docker compose -f docker-compose.test.yml down -v 2>/dev/null || true
}
trap cleanup EXIT

echo "=== Step 1: Generate server and tests ==="
uv run python generate.py

echo ""
echo "=== Step 2: Verify generated code parses ==="
uv run python -c "import ast; ast.parse(open('generated/server.py').read()); print('server.py: OK')"

echo ""
echo "=== Step 3: Start UniFi controller ==="
docker compose -f docker-compose.test.yml up -d

# Wait for /status to return "up":true (more reliable than Docker healthcheck)
echo "Waiting for controller to report up:true..."
for i in $(seq 1 60); do
    resp=$(curl -fsk "https://127.0.0.1:${PORT}/status" 2>/dev/null || true)
    if echo "$resp" | grep -q '"up":true'; then
        echo "Controller is UP (attempt $i)"
        break
    fi
    if [ "$i" -eq 60 ]; then
        echo "ERROR: Controller did not become ready within 300s"
        docker compose -f docker-compose.test.yml logs --tail=50
        exit 1
    fi
    sleep 5
done

echo ""
echo "=== Step 4: Seed admin user ==="
"$SCRIPT_DIR/seed_admin.sh" "$CONTAINER" "$USERNAME" "$PASSWORD"

# Poll until login actually works (may take a few seconds after seeding)
echo "Polling login endpoint..."
for i in $(seq 1 30); do
    code=$(curl -sk -o /dev/null -w '%{http_code}' \
        -X POST "https://127.0.0.1:${PORT}/api/login" \
        -H 'Content-Type: application/json' \
        -d "{\"username\":\"${USERNAME}\",\"password\":\"${PASSWORD}\"}")
    if [ "$code" = "200" ]; then
        echo "Login OK (attempt $i)"
        break
    fi
    if [ "$i" -eq 30 ]; then
        echo "ERROR: Login still failing after 30 attempts (HTTP $code)"
        exit 1
    fi
    sleep 3
done

echo ""
echo "=== Step 5: Run tests ==="
export UNIFI_HOST=127.0.0.1
export UNIFI_PORT="$PORT"
export UNIFI_USERNAME="$USERNAME"
export UNIFI_PASSWORD="$PASSWORD"
export UNIFI_SITE=default
export UNIFI_VERIFY_SSL=false
export UNIFI_REDACT_SECRETS=true

TEST_EXIT=0

# Module toggle tests (no controller needed)
echo "--- Module toggle tests ---"
uv run --extra test python -m pytest test_modules_toggle.py -v --timeout=300 "$@" || TEST_EXIT=$?

# Helper function + integration tests
echo "--- Integration tests (test_sprint_f.py) ---"
uv run --extra test python -m pytest tests/test_sprint_f.py -v --timeout=60 "$@" || TEST_EXIT=$?

# Generated tests (CRUD lifecycle, commands, globals)
echo "--- Generated tests ---"
uv run --extra test python -m pytest generated/tests/ -v --timeout=60 "$@" || TEST_EXIT=$?

echo ""
if [ "$TEST_EXIT" -eq 0 ]; then
    echo "=== All tests passed ==="
else
    echo "=== Some tests failed (exit code: $TEST_EXIT) ==="
fi

exit $TEST_EXIT
