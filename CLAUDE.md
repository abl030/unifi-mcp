# UniFi MCP Server Generator

## Goal

Build a **self-contained, auto-generated MCP server** for the UniFi Network Controller API. The server and its test suite are both generated from the API specification — not hand-maintained. When Ubiquiti updates their API, you bump a Docker image tag and re-run the generator.

## What's Already Here

This directory contains everything you need to understand the UniFi API surface:

- `endpoint-inventory.json` — Complete map of every discovered API endpoint with HTTP methods, live status codes, and record counts from a real v10.0.162 standalone controller
- `api-samples/` — Real (scrubbed) JSON responses from every working endpoint, giving you exact field names and types for schema inference
- `probe-spec.json` — Declarative list of ALL endpoints to probe (existing + community-discovered)
- `probe.py` — Single-file probe script that hammers a live controller to discover endpoints
- `scripts/run_probe.sh` — Automated: start container → seed admin → run probe → teardown

## API Surface (from endpoint-inventory.json)

Run `uv run python count_tools.py` to recompute these from the spec.

### Endpoints: 196 total (after probe + LLM probe)
- **37 REST** endpoints (17 existing + 20 community-discovered)
- **39 Stat** endpoints (18 existing + 21 community)
- **9 Cmd** managers with **68 commands** total
- **7 v2** endpoints (firewall policies, traffic rules, clients, ap groups, traffic routes, firewall zones)
- **8 Global** endpoints (status, self, sites, stat_sites, stat_admin, logout, system_poweroff, system_reboot)
- **34 List** endpoints (community — read-only `list/` prefix mirrors `rest/`)
- **2 Guest** endpoints (community — hotspot config/packages)
- **1 WebSocket** endpoint (community — events stream)
- Plus: 35 `set/setting/*` endpoints, 35 `get/setting/*` endpoints, 4 `cnt/*` endpoints, 2 `upd/*` endpoints, 1 `group/*` endpoint, 1 `dl/*` endpoint

### Generated Tools: 286 total
- **155 REST** tools (29 CRUD × 5 + settings × 3 + 5 read-only × 1)
- **39 Stat** tools (1 per stat endpoint)
- **68 Cmd** tools (1 per command across 9 managers)
- **15 v2** tools (7 resources, tools per HTTP method)
- **8 Global** tools (1 per global endpoint)
- **1 Port override** helper tool

## Architecture

### The Probe (`probe.py` + `probe-spec.json`)

A reusable endpoint discovery tool. When Ubiquiti releases a new controller version, re-run the probe to discover new/changed/removed endpoints:

```bash
# Full automated cycle (start container, seed admin, probe, teardown):
scripts/run_probe.sh

# Or manually against a running controller:
uv run python probe.py --host HOST --username admin --password pass --no-verify-ssl

# Preview what would be probed:
uv run python probe.py --dry-run
```

**Safety rules (hardcoded):** Never POST/PUT/DELETE to rest/, never execute unsafe commands, never hit system/reboot or poweroff. Only 4 safe commands executed: `speedtest-status`, `get-admins`, `list-backups`, `check-firmware-update`.

**Sample scrubbing:** All sensitive fields (`x_password`, `x_passphrase`, `x_shadow`, `x_private_key`, etc.) are replaced with `"REDACTED"` before writing to disk.

**Output:** Updates `endpoint-inventory.json` (same schema as before, plus new categories: `list_endpoints`, `guest_endpoints`, `websocket_endpoints`) and writes sample files to `api-samples/`.

### The Generator (`generate.py`)

A single script that reads `endpoint-inventory.json` + `api-samples/*.json` and outputs:

1. **`server.py`** — A complete FastMCP server with one tool per API operation:
   - `rest/*` endpoints → `list_{resource}`, `get_{resource}`, `create_{resource}`, `update_{resource}`, `delete_{resource}` tools
   - `stat/*` endpoints → `get_{stat}` / `list_{stat}` tools
   - `cmd/*` endpoints → `{command}_{manager}` tools (e.g. `restart_device`, `block_client`)
   - `v2/*` endpoints → corresponding CRUD tools
   - Every mutation tool requires `confirm=true` (safety gate)
   - Every tool has proper parameter types inferred from the sample data
   - Tools include docstrings generated from endpoint descriptions

2. **`tests/`** — A pytest suite with:
   - Full CRUD lifecycle tests for every REST resource (create → read → verify → update → verify → delete → verify gone)
   - Read-only tests for stat endpoints (call and validate response structure)
   - Command tests where safe (e.g. locate/unlocate, not reboot)
   - All tests run against a real ephemeral UniFi controller (see below)

3. **`conftest.py`** — Pytest fixtures that:
   - Spin up a UniFi controller Docker container (use `jacobalberty/unifi-docker:latest` or similar)
   - Wait for healthy (poll `/status` endpoint)
   - Run initial setup (create site, set admin credentials) via the API
   - Provide authenticated session to all tests
   - Tear down on completion

### The MCP Server (`server.py`)

- Uses **FastMCP** (same framework as the current hand-maintained server)
- Single `UniFiClient` class handles auth, session management, cookie handling
- Supports both standalone controllers and UniFi OS (with/without `/proxy/network` prefix)
- Environment variables for configuration: `UNIFI_HOST`, `UNIFI_USERNAME`, `UNIFI_PASSWORD`, `UNIFI_PORT`, `UNIFI_SITE`, `UNIFI_VERIFY_SSL`
- Graceful error handling with clear error messages in tool responses

### Docker Test Harness

The test suite is fully self-contained:
- `docker-compose.test.yml` defines the ephemeral UniFi controller
- `conftest.py` manages lifecycle (or use `testcontainers-python`)
- No external dependencies — `pytest` does everything
- Tests are idempotent and isolated (each test creates/cleans its own resources)

## API Pattern Reference

### Authentication
```
POST /api/login {"username": "...", "password": "..."}
# Returns Set-Cookie header with unifises and csrf_token
# All subsequent requests send cookies + X-Csrf-Token header
```

### REST CRUD Pattern
```
GET    /api/s/{site}/rest/{resource}          → list all
GET    /api/s/{site}/rest/{resource}/{_id}    → get one (some endpoints)
POST   /api/s/{site}/rest/{resource}          → create (body = resource fields)
PUT    /api/s/{site}/rest/{resource}/{_id}    → update (body = changed fields)
DELETE /api/s/{site}/rest/{resource}/{_id}    → delete
```

Response format: `{"meta": {"rc": "ok"}, "data": [...]}`
Error format: `{"meta": {"rc": "error", "msg": "..."}, "data": []}`

### Stat Pattern (read-only)
```
GET  /api/s/{site}/stat/{resource}
POST /api/s/{site}/stat/{resource}  (some support filtering via POST body)
```

### Command Pattern
```
POST /api/s/{site}/cmd/{manager} {"cmd": "command-name", ...extra_params}
```

### List Pattern (read-only, mirrors REST)
```
GET /api/s/{site}/list/{resource}
```
Returns same data as `rest/` but read-only. Useful for bulk reads without mutation risk.

### v2 API Pattern
```
GET/POST/PUT/DELETE /v2/api/site/{site}/{resource}
```

### Guest Pattern
```
GET /guest/s/{site}/{resource}
```

## Key Resources and Their Schemas

Refer to `api-samples/` for exact field structures. Key ones:

- **rest/networkconf** — Networks/VLANs: `name`, `purpose` (corporate/guest), `vlan_enabled`, `ip_subnet`, `dhcpd_*`
- **rest/portconf** — Switch port profiles: `name`, `forward`, `native_networkconf_id`, `tagged_vlan_mgmt`, `poe_mode`
- **rest/wlanconf** — WiFi networks: `name`, `security`, `wpa_mode`, `networkconf_id`, `enabled`
- **rest/firewallrule** — Firewall rules: `name`, `action`, `ruleset`, `src_*`, `dst_*`, `protocol`
- **rest/firewallgroup** — IP/port groups for firewall rules
- **rest/portforward** — Port forwards: `name`, `fwd`, `fwd_port`, `dst_port`, `proto`
- **rest/setting** — Site settings (38 categories, keyed by `key` field)
- **stat/device** — Full device details including `port_table` (switch port status, PoE, clients)
- **stat/sta** — Connected clients with IP, MAC, signal, traffic stats
- **rest/user** — Known clients (seen historically)

## Device Port Override Pattern

This is the specific use case that motivated this project — configuring switch ports via API:

```python
# PUT /api/s/{site}/rest/device/{device_id}
{
    "port_overrides": [
        {
            "port_idx": 3,
            "portconf_id": "{port_profile_id}",  # from rest/portconf
            # OR inline overrides:
            "name": "Server Port",
            "forward": "customize",
            "native_networkconf_id": "{network_id}"
        }
    ]
}
```

## Critical Rule: Never Touch Generated Code

**NEVER, under any circumstances, manually edit the generated output files** (`server.py`, `tests/`, `conftest.py`, or any other file produced by the generator). We are testing the automated generator itself — if the generated code has bugs, the fix MUST be made in the generator so that re-running it produces correct output. Hand-patching generated files defeats the entire purpose of this project.

## Implementation Notes

- **Schema inference**: Use the sample JSON files to infer types. `_id` is always string. Booleans, integers, strings are obvious from values. Fields ending in `_enabled` are bool. Fields ending in `_id` are string references.
- **Tool naming**: Use `unifi_` prefix for all tools. Use snake_case. Be explicit: `unifi_list_networks` not `unifi_networks`.
- **Confirmation gate**: All create/update/delete operations must require `confirm=true`. Return a preview of what would change when `confirm` is missing or false.
- **Site awareness**: Default site to env var, but allow per-tool override.
- **Error handling**: Parse the `meta.rc` and `meta.msg` fields. Return clear, actionable error messages.
- **Docker controller setup**: The UniFi controller takes ~60-90s to start. The setup wizard is bypassed by seeding an admin directly into MongoDB (see `scripts/seed_admin.sh`). Key gotchas:
  - Use `db.admin.insert()` not `insertOne()` (the latter silently fails on older mongo shells)
  - Must also insert `privilege` records for each site
  - The `/status` endpoint returns `"up": true` when ready (don't check `server_running` — it may not exist)
  - Login may return 400 for a few seconds after seeding; poll until 200
- **Adding new REST resources to the generator**: When the probe discovers new REST endpoints, they won't generate tools until added to `RESOURCE_NAMES` in `generator/naming.py`. The template (`server.py.j2`) silently skips REST resources not in `RESOURCE_NAMES` (there is no `{% else %}` fallback). Run `count_tools.py` to see which are skipped.

## Tech Stack

- **Python 3.11+**
- **FastMCP** for the MCP server framework
- **httpx** for async HTTP client (or requests if sync is simpler)
- **pytest** + **testcontainers** (or docker-compose) for integration tests
- **Jinja2** or AST-based code generation
- **pyproject.toml** for packaging

## LLM Probe (`llm-probe/`)

Uses `claude -p` (Claude Code CLI) to reason about unconfirmed endpoints — trying different HTTP methods, bodies, and path variations. No Python dependencies beyond stdlib; just needs `claude` and `curl` on PATH.

```bash
# Dry run (show what would be probed):
python llm-probe/llm_probe.py --dry-run

# Probe all 400-status endpoints (highest value — they definitely exist):
python llm-probe/llm_probe.py --host localhost --port 8443 \
    --username admin --password testpassword123 \
    --no-verify-ssl --only-category 400

# Probe 404 endpoints:
python llm-probe/llm_probe.py --only-category 404 ...

# Limit for testing:
python llm-probe/llm_probe.py --max-endpoints 5 ...
```

**Results (v10.0.162, 86 endpoints probed):**
- **44 FOUND** — newly confirmed working endpoints
- **28 NOT_FOUND** — don't exist on this version
- **11 NEEDS_DEVICE** — exist but require adopted hardware
- **3 UNCERTAIN** — ambiguous results

Key discoveries:
- All 28 `set/setting/*` endpoints confirmed as PUT-only (read via `get/setting/*`, write via `set/setting/*`)
- `stat/session` needs POST with `{"type":"all","start":0,"end":9999999999}`
- `upd/user` works via PUT with user `_id`
- `group/user` is a batch endpoint: POST with `{"objects":[{"data":{...}}]}`
- `websocket/events` at `/wss/s/{site}/events` accepts WebSocket upgrade
- `rest/device` needs a device `_id` suffix (no bare GET)
- `upd/device` exists and works with PUT/POST (needs adopted device)
- 66 unverified commands still untested (need `--only-category cmd`)

Output: `llm-probe/discoveries.json` (merged), `llm-probe/discoveries-400.json`, `llm-probe/discoveries-404.json`

## TODO: Full Test Coverage with Device Simulation

The current test harness runs against a bare controller (no adopted devices), which means 11+ endpoints that `NEEDS_DEVICE` can't be tested. Options to explore:

1. **Mock device adoption via MongoDB**: Seed fake device documents into the controller's MongoDB. The UniFi container uses MongoDB internally — we can `docker exec` into it and insert device records (type=usw/uap/ugw, mac, model, adopted=true, etc.). If the controller's internal state accepts these, stat/device, rest/device, upd/device, list/devices, list/firmware, stat/gateway, cnt/sta, and list/wifichannels may all start returning data. This is the cheapest approach (no hardware needed) but may not work if the controller validates device heartbeats.

2. **UniFi device simulator**: Build a minimal service that speaks the UniFi inform protocol (AES-encrypted JSON over HTTP to port 8080). A simulated AP/switch would:
   - POST to `/inform` with device stats (model, MAC, firmware, uptime)
   - Accept provisioning responses from the controller
   - Show up in stat/device and be manageable via rest/device
   This is the most realistic approach and would unblock all device-dependent endpoints. The inform protocol is documented by the community (see `unifi-inform-protocol` repos).

3. **Buy a physical device**: A UniFi Flex Mini (~$30) or USW-Lite-8-PoE (~$110) would provide a real device for testing. This gives full end-to-end coverage including port_overrides (the original motivation), PoE control, LED management, and firmware commands. Downside: requires network setup, device is dedicated to testing.

4. **Hybrid approach**: Use MongoDB seeding for basic presence (so list/stat endpoints return data), then use a device simulator for testing mutation endpoints (port overrides, locate/unlocate, config changes). Physical device only needed for final validation of the full flow.

Priority order: Try option 1 first (free, fast), then option 2 if MongoDB seeding doesn't convince the controller. Option 3 is the nuclear option for full confidence.

## Excluded Endpoints (LLM Probe Results)

Endpoints tested by the LLM probe that were NOT_FOUND or UNCERTAIN on v10.0.162. These are excluded from `endpoint-inventory.json` and tool generation.

### NOT_FOUND (28 endpoints)

| Category | Endpoint | Reason |
|----------|----------|--------|
| global | self_profile | Does not exist; use `/api/self` instead |
| global | auth_login | UniFi OS-only; standalone uses `/api/login` |
| global | users_self | UniFi OS-only; standalone uses `/api/self` |
| rest | apgroup | Superseded by `v2/api/site/{site}/apgroups` |
| rest | dashboard | Use `stat/dashboard` instead |
| list | apgroup | Use v2 apgroups endpoint instead |
| list | backup | Use `cmd/backup list-backups` instead |
| list | rogueap | Use `stat/rogueap` instead |
| list | radiusaccount | Use `rest/radiusprofile` instead |
| list | broadcastgroup | Resource type not available on v10.0.162 |
| list | extension | Requires extensions/plugins not installed |
| list | country | Not implemented in v10.0.162 |
| list | settings | Typo — correct is `list/setting` (singular) |
| list | mediafile | Resource type not recognized |
| list | element | Resource type not available |
| list | admin | Use `cmd/sitemgr get-admins` instead |
| list | device | Use `stat/device` instead |
| list | dashboard | Use `stat/dashboard` instead |
| stat | syslog | Not implemented in v10.0.162 |
| stat | speedtest | Use `stat/report/archive.speedtest` instead |
| stat | ips_events | Typo — correct is `stat/ips/event` (singular) |
| stat | sessions | Typo — correct is `stat/session` (singular) |
| stat | sta_sessions | Not implemented in v10.0.162 |
| stat | auths | Not implemented in v10.0.162 |
| stat | allusers | Typo — correct is `stat/alluser` (singular) |
| stat | user_sessions | Not implemented in v10.0.162 |
| stat | status | Not implemented; `/status` is global only |
| stat | stream | May be UniFi OS-specific or deprecated |

### UNCERTAIN (3 endpoints)

| Category | Endpoint | Reason |
|----------|----------|--------|
| global | auth_logout | Exists on route table but needs unknown params; may be UniFi OS only |
| v2 | fingerprint_devices | Returns 400 consistently; may need fingerprinting feature enabled |
| set | setting/auto_speedtest | GET works but PUT returns 500; feature may not be fully implemented |

## Stretch Goals

- **Live spec discovery**: If running against a UniFi OS controller that serves `/api-docs/integration.json`, pull the spec at startup and register tools dynamically (no generator needed)
- **Schema validation**: Generate Pydantic models from samples for request/response validation
- **Diff detection**: Compare generated output against previous run, highlight new/removed/changed endpoints

## Getting Started

1. Read `endpoint-inventory.json` to understand the full API surface
2. Read a few `api-samples/*.json` files to understand response shapes
3. Build the generator that produces the MCP server + tests
4. Get the server running locally first (`uvx` or `python -m server`)
5. Then build out the Docker test harness
6. Run tests until green

### Updating the API surface

```bash
# Re-probe a live controller (automated):
scripts/run_probe.sh

# Then regenerate:
uv run python generate.py

# Verify counts match:
uv run python count_tools.py
```

### Docker setup

Docker must be enabled on NixOS: add `virtualisation.docker.enable = true;` to `/etc/nixos/configuration.nix` and rebuild. User must be in the `docker` group.

If the docker socket path is wrong (e.g. trying podman), set `DOCKER_HOST=unix:///var/run/docker.sock`.
