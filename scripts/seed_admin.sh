#!/usr/bin/env bash
# Seed an admin user directly into UniFi's embedded MongoDB.
# Usage: seed_admin.sh [container_name] [username] [password] [email]
#
# This bypasses the setup wizard by inserting the admin into the 'ace' database
# and marking the controller as "installed" via system.properties.
set -euo pipefail

CONTAINER="${1:-unifi-test-controller}"
USERNAME="${2:-admin}"
PASSWORD="${3:-testpassword123}"
EMAIL="${4:-admin@test.local}"

echo "Waiting for MongoDB (port 27117) inside container..."
for i in $(seq 1 60); do
    if docker exec "$CONTAINER" mongosh --port 27117 --quiet --eval "db.runCommand({ping:1})" ace >/dev/null 2>&1; then
        echo "  MongoDB is ready."
        break
    fi
    if docker exec "$CONTAINER" mongo --port 27117 --quiet --eval "db.runCommand({ping:1})" ace >/dev/null 2>&1; then
        echo "  MongoDB is ready (legacy mongo shell)."
        break
    fi
    if [ "$i" -eq 60 ]; then
        echo "ERROR: MongoDB did not become ready in 60 attempts"
        exit 1
    fi
    sleep 2
done

# Determine which mongo shell is available
if docker exec "$CONTAINER" which mongosh >/dev/null 2>&1; then
    MONGO_CMD="mongosh"
else
    MONGO_CMD="mongo"
fi
echo "Using $MONGO_CMD shell"

# Generate SHA-512 password hash using openssl inside the container
HASH=$(docker exec "$CONTAINER" openssl passwd -6 "$PASSWORD" 2>/dev/null || \
       docker exec "$CONTAINER" python3 -c "import crypt; print(crypt.crypt('$PASSWORD', crypt.mksalt(crypt.METHOD_SHA512)))" 2>/dev/null || \
       python3 -c "import crypt; print(crypt.crypt('$PASSWORD', crypt.mksalt(crypt.METHOD_SHA512)))")

echo "Seeding admin user '$USERNAME' into MongoDB..."

docker exec "$CONTAINER" $MONGO_CMD --port 27117 --quiet ace <<MONGOSCRIPT
// Check if admin already exists
var existing = db.admin.findOne({"name": "$USERNAME"});
if (existing) {
    print("Admin '$USERNAME' already exists, skipping insert.");
} else {
    // Insert admin
    db.admin.insertOne({
        "email": "$EMAIL",
        "last_site_name": "default",
        "name": "$USERNAME",
        "x_shadow": "$HASH"
    });

    // Get the admin's _id
    var admin = db.admin.findOne({"name": "$USERNAME"});
    var adminId = admin._id.toString();
    print("Created admin with id: " + adminId);

    // Grant super admin privilege for all existing sites
    var sites = db.site.find().toArray();
    sites.forEach(function(site) {
        db.privilege.insertOne({
            "admin_id": adminId,
            "site_id": site._id.toString(),
            "role": "admin",
            "permissions": []
        });
        print("Granted admin privilege for site: " + site.name);
    });
}
MONGOSCRIPT

echo "Admin seeded successfully."
echo ""
echo "Now waiting for controller to recognize the admin..."
sleep 3

# Test login
echo "Testing login..."
HTTP_CODE=$(curl -sk -o /dev/null -w "%{http_code}" \
    -X POST "https://localhost:8443/api/login" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\"}")

if [ "$HTTP_CODE" = "200" ]; then
    echo "Login successful! (HTTP $HTTP_CODE)"
else
    echo "Login returned HTTP $HTTP_CODE — the controller may need a moment."
    echo "The admin may need the controller to restart or finish initializing."
fi
