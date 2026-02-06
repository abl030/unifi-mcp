#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

echo "=== Step 1: Generate server and tests ==="
uv run python generate.py

echo ""
echo "=== Step 2: Verify generated code parses ==="
uv run python -c "import ast; ast.parse(open('generated/server.py').read()); print('server.py: OK')"

echo ""
echo "=== Step 3: Start UniFi controller ==="
docker compose -f docker-compose.test.yml up -d
echo "Waiting for controller to become healthy..."

# Wait for health check
for i in $(seq 1 36); do
    if docker compose -f docker-compose.test.yml ps --format json | grep -q '"healthy"'; then
        echo "Controller is healthy!"
        break
    fi
    if [ "$i" -eq 36 ]; then
        echo "ERROR: Controller did not become healthy within 180s"
        docker compose -f docker-compose.test.yml logs --tail=50
        docker compose -f docker-compose.test.yml down -v
        exit 1
    fi
    sleep 5
done

echo ""
echo "=== Step 4: Run tests ==="
export UNIFI_HOST=localhost
export UNIFI_PORT=8443
export UNIFI_USERNAME=admin
export UNIFI_PASSWORD=testpassword123

cd generated
uv run pytest tests/ -v --timeout=60 "$@"
TEST_EXIT=$?
cd "$PROJECT_DIR"

echo ""
echo "=== Step 5: Cleanup ==="
docker compose -f docker-compose.test.yml down -v

exit $TEST_EXIT
