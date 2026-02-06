# UniFi MCP Server Generator

## Goal

Build a **self-contained, auto-generated MCP server** for the UniFi Network Controller API. The server and its test suite are both generated from the API specification — not hand-maintained. When Ubiquiti updates their API, you bump a Docker image tag and re-run the generator.

## What's Already Here

This directory contains everything you need to understand the UniFi API surface:

- `endpoint-inventory.json` — Complete map of every discovered API endpoint (REST CRUD, stat reads, command endpoints, v2 endpoints) with HTTP methods, live status codes, and record counts from a real v10.0.162 standalone controller
- `api-samples/` — Real (scrubbed) JSON responses from every working endpoint, giving you exact field names and types for schema inference
- `community-swagger.yaml` — Community-maintained OpenAPI spec fragment (incomplete but useful reference)

## Architecture

### The Generator (`generate.py` or similar)

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

### v2 API Pattern
```
GET/POST/PUT/DELETE /v2/api/site/{site}/{resource}
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
- **Docker controller setup**: The UniFi controller takes ~60-90s to start. The setup wizard needs to be completed via API before tests can run. Research the setup/wizard API endpoints.

## Tech Stack

- **Python 3.11+**
- **FastMCP** for the MCP server framework
- **httpx** for async HTTP client (or requests if sync is simpler)
- **pytest** + **testcontainers** (or docker-compose) for integration tests
- **Jinja2** or AST-based code generation
- **pyproject.toml** for packaging

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

Docker is available via NixOS — if you need to add it, add `virtualisation.docker.enable = true;` to the NixOS config or use podman.
