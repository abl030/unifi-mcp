#!/usr/bin/env bash
# Start an ephemeral UniFi controller, seed an admin, and run the probe.
# Usage: scripts/run_probe.sh [--keep]   (--keep skips teardown)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

CONTAINER="unifi-test-controller"
USERNAME="admin"
PASSWORD="testpassword123"
KEEP=false

for arg in "$@"; do
    if [ "$arg" = "--keep" ]; then KEEP=true; fi
done

cleanup() {
    if [ "$KEEP" = false ]; then
        echo ""
        echo "=== Cleanup ==="
        docker compose -f docker-compose.test.yml down -v
    else
        echo ""
        echo "Container kept running. Tear down with: docker compose -f docker-compose.test.yml down -v"
    fi
}
trap cleanup EXIT

# ── Step 1: Start controller ────────────────────────────────────────────────
echo "=== Step 1: Start UniFi controller ==="
docker compose -f docker-compose.test.yml up -d

echo "Waiting for container to become healthy..."
for i in $(seq 1 36); do
    if docker compose -f docker-compose.test.yml ps --format json | grep -q '"healthy"'; then
        echo "  Container is healthy."
        break
    fi
    if [ "$i" -eq 36 ]; then
        echo "ERROR: Controller did not become healthy within 180s"
        docker compose -f docker-compose.test.yml logs --tail=50
        exit 1
    fi
    sleep 5
done

# ── Step 2: Seed admin via MongoDB ──────────────────────────────────────────
echo ""
echo "=== Step 2: Seed admin user ==="

# Wait for MongoDB
echo "Waiting for MongoDB (port 27117)..."
for i in $(seq 1 60); do
    if docker exec "$CONTAINER" mongo --port 27117 --quiet --eval "db.runCommand({ping:1})" ace >/dev/null 2>&1; then
        MONGO_CMD="mongo"
        echo "  MongoDB is ready (mongo shell)."
        break
    fi
    if docker exec "$CONTAINER" mongosh --port 27117 --quiet --eval "db.runCommand({ping:1})" ace >/dev/null 2>&1; then
        MONGO_CMD="mongosh"
        echo "  MongoDB is ready (mongosh shell)."
        break
    fi
    if [ "$i" -eq 60 ]; then
        echo "ERROR: MongoDB did not become ready"
        exit 1
    fi
    sleep 2
done

# Generate password hash
HASH=$(docker exec "$CONTAINER" openssl passwd -6 "$PASSWORD" 2>/dev/null || \
       python3 -c "import crypt; print(crypt.crypt('$PASSWORD', crypt.mksalt(crypt.METHOD_SHA512)))")

# Insert admin + grant privileges
echo "Inserting admin user..."
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

# ── Step 3: Wait for login to work ─────────────────────────────────────────
echo ""
echo "=== Step 3: Wait for login ==="
for i in $(seq 1 30); do
    HTTP_CODE=$(curl -sk -o /dev/null -w "%{http_code}" \
        -X POST "https://localhost:8443/api/login" \
        -H "Content-Type: application/json" \
        -d "{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\"}")
    if [ "$HTTP_CODE" = "200" ]; then
        echo "  Login works! (HTTP 200)"
        break
    fi
    if [ "$i" -eq 30 ]; then
        echo "ERROR: Login still failing after 60s (HTTP $HTTP_CODE)"
        exit 1
    fi
    sleep 2
done

# ── Step 4: Run probe ──────────────────────────────────────────────────────
echo ""
echo "=== Step 4: Run probe ==="
uv run python probe.py \
    --host localhost \
    --port 8443 \
    --username "$USERNAME" \
    --password "$PASSWORD" \
    --no-verify-ssl \
    "$@"

echo ""
echo "=== Done ==="
echo "Updated: endpoint-inventory.json"
echo "Samples: api-samples/"
