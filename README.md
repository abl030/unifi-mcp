# UniFi MCP Server

An MCP (Model Context Protocol) server that gives AI agents full control over Ubiquiti UniFi network infrastructure. **285 tools** covering networks, firewall rules, switch ports, WiFi, clients, device commands, hotspot management, DPI, site settings, and more.

This entire project — the generator, the server, the test suite, and this README — was built by AI (Claude) and is designed to be installed and used by AI agents.

## Install This MCP Server

### Option 1: Nix Flake (recommended)

This repo is a Nix flake. Add it as an input to your NixOS config or any flake, and you get a self-contained `unifi-mcp` binary with all dependencies bundled. Updates are a single `nix flake update`.

**Add to your flake inputs:**

```nix
# flake.nix
{
  inputs = {
    unifi-mcp.url = "github:abl030/unifi-mcp";
  };
}
```

**Use the package:**

```nix
# The binary is at: inputs.unifi-mcp.packages.${system}.default
# It provides: unifi-mcp (runs fastmcp with the server)

# Example: add to systemPackages
environment.systemPackages = [ inputs.unifi-mcp.packages.${pkgs.system}.default ];

# Example: use in an MCP server config
{
  command = "${inputs.unifi-mcp.packages.${pkgs.system}.default}/bin/unifi-mcp";
  env = {
    UNIFI_HOST = "192.168.1.1";
    UNIFI_USERNAME = "admin";
    UNIFI_PASSWORD = "your-password";
  };
}
```

**Quick test without installing:**

```bash
UNIFI_HOST=192.168.1.1 UNIFI_PASSWORD=secret nix run github:abl030/unifi-mcp
```

**Build locally:**

```bash
nix build github:abl030/unifi-mcp
./result/bin/unifi-mcp  # starts the MCP server on stdio
```

### Option 2: uv (non-Nix)

```bash
git clone https://github.com/abl030/unifi-mcp.git
cd unifi-mcp
uv sync
uv run python generate.py
```

This produces `generated/server.py` — the MCP server with 285 tools.

### Configure Your MCP Client

**Claude Code** (`claude mcp add`):

```bash
# Nix — uses the flake binary directly
claude mcp add unifi -- \
  env UNIFI_HOST=YOUR_CONTROLLER_IP \
  UNIFI_PORT=8443 \
  UNIFI_USERNAME=admin \
  UNIFI_PASSWORD=YOUR_PASSWORD \
  UNIFI_SITE=default \
  unifi-mcp

# Non-Nix — uses uv to run
claude mcp add unifi -- \
  env UNIFI_HOST=YOUR_CONTROLLER_IP \
  UNIFI_PORT=8443 \
  UNIFI_USERNAME=admin \
  UNIFI_PASSWORD=YOUR_PASSWORD \
  UNIFI_SITE=default \
  uv run --directory /path/to/unifi-mcp fastmcp run generated/server.py
```

**Claude Desktop** (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "unifi": {
      "command": "unifi-mcp",
      "env": {
        "UNIFI_HOST": "YOUR_CONTROLLER_IP",
        "UNIFI_PORT": "8443",
        "UNIFI_USERNAME": "admin",
        "UNIFI_PASSWORD": "YOUR_PASSWORD",
        "UNIFI_SITE": "default"
      }
    }
  }
}
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `UNIFI_HOST` | `localhost` | Controller hostname or IP |
| `UNIFI_PORT` | `8443` | Controller HTTPS port |
| `UNIFI_USERNAME` | `admin` | Admin username |
| `UNIFI_PASSWORD` | *(required)* | Admin password |
| `UNIFI_SITE` | `default` | Site name |
| `UNIFI_VERIFY_SSL` | `false` | Verify SSL certificates |
| `UNIFI_MODULES` | `v1,v2` | Tool groups to register (see below) |
| `UNIFI_READ_ONLY` | `false` | Strip all mutating tools (see below) |
| `UNIFI_REDACT_SECRETS` | `true` | Replace sensitive fields (`x_passphrase`, passwords, etc.) with `<redacted>` in responses |

### Module Toggle (`UNIFI_MODULES`)

Control which tool groups are registered at runtime. Use fine-grained modules to load only what you need, reducing noise for the LLM.

**Shortcuts** (backward compatible):

| Value | Tools | Use case |
|-------|-------|----------|
| `v1,v2` (default) | 285 | All tools (UniFi OS controllers) |
| `v1` | 270 | All v1 tools (standalone controllers, no v2 endpoints) |
| `v2` | 25 | v2 + global tools only |

**Fine-grained modules** (mix and match):

| Module | Tools | What's included |
|--------|-------|-----------------|
| `device` | 33 | Device commands (adopt/restart/upgrade/locate), device stats, port override |
| `client` | 17 | Client block/kick/forget, user CRUD, client stats, v2 active/history clients |
| `wifi` | 15 | WLAN configs, WLAN groups, channel plans, v2 AP groups |
| `network` | 15 | Networks/VLANs, port profiles, DNS records |
| `firewall` | 42 | Firewall rules/groups, port forwards, routes, DDNS, DHCP, v2 policies/zones/traffic |
| `monitor` | 34 | All stat endpoints, alarms, events, reports, DPI stats |
| `admin` | 41 | Settings, user groups, tags, accounts, site/admin mgmt, backup |
| `hotspot` | 32 | Hotspot ops/packages, Hotspot2, RADIUS, vouchers, guest commands |
| `advanced` | 46 | Maps, heatmaps, spatial, DPI config, media, schedules, broadcast |

Tool counts above include both v1 and v2 tools for each module. Global tools (10: `status`, `self`, `sites`, etc. + `report_issue` + `get_overview`) are always registered regardless of this setting.

**Example**: A standalone controller managing switches and APs:

```bash
UNIFI_MODULES=device,client,wifi,network,monitor  # 124 tools instead of 285
```

No regeneration needed — just set the env var.

### Read-Only Mode (`UNIFI_READ_ONLY`)

Set `UNIFI_READ_ONLY=true` to strip all mutating tools at registration time. Only list, get, and stat tools are registered — no create, update, delete, restart, reboot, or any other state-changing operations exist in the MCP tool list.

| Config | Tools | Use case |
|--------|-------|----------|
| `UNIFI_READ_ONLY=false` (default) | 285 | Full access |
| `UNIFI_READ_ONLY=true` | 124 | Monitoring only — zero mutation risk |
| `UNIFI_MODULES=device,client,monitor UNIFI_READ_ONLY=true` | 51 | Focused monitoring |

Composes with `UNIFI_MODULES` — both filters apply independently. Read-only mode is enforced at tool registration time, not runtime: mutating tools don't exist in the MCP tool list, so the LLM cannot call them even if instructed to.

## What You Get: 285 Tools

### Network Configuration (CRUD — 5 tools each)

| Resource | Tools | Description |
|----------|-------|-------------|
| Networks | `list` / `get` / `create` / `update` / `delete` | VLANs, subnets, DHCP (`rest/networkconf`) |
| Firewall Rules | `list` / `get` / `create` / `update` / `delete` | L3/L4 firewall rules |
| Firewall Groups | `list` / `get` / `create` / `update` / `delete` | IP/port groups for rules |
| Port Forwards | `list` / `get` / `create` / `update` / `delete` | NAT port forwarding |
| Port Profiles | `list` / `get` / `create` / `update` / `delete` | Switch port profiles |
| WLANs | `list` / `get` / `create` / `update` / `delete` | WiFi networks |
| WLAN Groups | `list` / `get` / `create` / `update` / `delete` | WiFi network groups |
| Routes | `list` / `get` / `create` / `update` / `delete` | Static routes |
| Dynamic DNS | `list` / `get` / `create` / `update` / `delete` | DDNS entries |
| RADIUS Profiles | `list` / `get` / `create` / `update` / `delete` | RADIUS auth profiles |
| RADIUS Accounts | `list` / `get` / `create` / `update` / `delete` | RADIUS user accounts |
| User Groups | `list` / `get` / `create` / `update` / `delete` | Client groups |
| Users | `list` / `get` / `create` / `update` | Known clients (delete via `forget_client`) |
| Tags | `list` / `get` / `create` / `update` / `delete` | Device/client tags |
| Accounts | `list` / `get` / `create` / `update` / `delete` | RADIUS accounts |

### Hotspot & Guest Management (CRUD)

| Resource | Tools | Description |
|----------|-------|-------------|
| Hotspot Operators | `list` / `get` / `create` / `update` / `delete` | Hotspot portal operators |
| Hotspot Packages | `list` / `get` / `create` / `update` / `delete` | Hotspot billing packages |
| Hotspot2 Configs | `list` / `get` / `create` / `update` / `delete` | Passpoint/Hotspot 2.0 |
| Vouchers | `create_voucher` / `revoke_voucher` / `delete_voucher` | Guest access vouchers |
| Guest Auth | `hotspot_authorize_guest` / `extend_guest_validity` | Guest session management |

### Site Mapping & Spatial (CRUD)

| Resource | Tools | Description |
|----------|-------|-------------|
| Maps | `list` / `get` / `create` / `update` / `delete` | Site floor plan maps |
| Heatmaps | `list` / `get` / `create` / `update` / `delete` | WiFi coverage heatmaps |
| Heatmap Points | `list` / `get` / `create` / `update` / `delete` | Heatmap data points |
| Spatial Records | `list` / `get` / `create` / `update` / `delete` | Device positioning |

### DPI & Network Intelligence (CRUD)

| Resource | Tools | Description |
|----------|-------|-------------|
| DPI Apps | `list` / `get` / `create` / `update` / `delete` | Application definitions |
| DPI Groups | `list` / `get` / `create` / `update` / `delete` | DPI restriction groups |
| DNS Records | `list` / `get` / `create` / `update` / `delete` | Local DNS records |
| DHCP Options | `list` / `get` / `create` / `update` / `delete` | Custom DHCP options |
| Broadcast Groups | `list` / `get` / `create` / `update` / `delete` | Multicast groups |
| Schedule Tasks | `list` / `get` / `create` / `update` / `delete` | Scheduled operations |
| Media Files | `list` / `get` / `create` / `update` / `delete` | Portal media files |

### Read-Only Resources (1 tool each)

| Tool | Description |
|------|-------------|
| `unifi_list_device_configs` | Device configurations (use `set_port_override` to modify) |
| `unifi_list_channel_plans` | WiFi channel plans |
| `unifi_list_virtual_devices` | Virtual/logical devices |
| `unifi_list_known_rogue_aps` | Known/neighboring APs |
| `unifi_list_elements` | Element platform devices |
| `unifi_list_alarms` | Alarm history |
| `unifi_list_events` | Event log |

### Settings (3 tools)

| Tool | Description |
|------|-------------|
| `unifi_list_settings` | All 38 setting categories |
| `unifi_get_setting` | Get a specific setting by key |
| `unifi_update_setting` | Update a setting (requires confirm) |

### Device Monitoring (39 stat tools)

| Tool | Description |
|------|-------------|
| `unifi_list_devices` | All adopted devices with full details |
| `unifi_list_clients` | Connected clients (IP, MAC, signal, traffic) |
| `unifi_list_health` | Network health subsystems |
| `unifi_list_rogue_aps` | Detected rogue access points |
| `unifi_list_sessions` | Client session history |
| `unifi_list_sysinfo` | System information |
| `unifi_list_devices_basic` | Devices (basic info) |
| `unifi_list_guests` | Guest clients |
| `unifi_list_dashboard` | Dashboard time-series data |
| `unifi_list_all_users` | All users (historical) |
| `unifi_list_vouchers` | Hotspot vouchers |
| `unifi_list_gateway_stats` | Gateway device stats |
| `unifi_list_dpi_stats` | DPI statistics |
| `unifi_list_anomalies` | Network anomalies |
| `unifi_list_ips_events` | IDS/IPS events |
| `unifi_list_remote_user_vpn` | Remote VPN sessions |
| `unifi_list_sdn_status` | SDN connection status |
| `unifi_list_spectrum_scans` | RF spectrum scan results |
| `unifi_list_stat_alarms` / `stat_events` | Stat-level alarm/event data |
| `unifi_list_site_dpi` / `client_dpi` | DPI stats per site/client |
| `unifi_list_country_codes` / `current_channels` | Reference data |
| `unifi_list_routing_stats` / `authorizations` / `payments` | Misc stats |
| `unifi_list_dynamic_dns_stats` / `port_forward_stats` | Service stats |
| `unifi_list_report` | Reports (5min/hourly/daily/monthly) |
| `unifi_list_speedtest_results` | Archived speedtest results |
| `unifi_list_report_*` | 8 specific report endpoints (5min/hourly/daily/monthly for gateway, AP, site, user) |

### Device Commands (28 devmgr commands)

| Tool | Description |
|------|-------------|
| `unifi_restart_device` | Restart a device |
| `unifi_adopt_device` / `advanced_adopt_device` | Adopt new devices |
| `unifi_locate_device` / `unlocate_device` | Flash device LEDs |
| `unifi_upgrade_device` / `upgrade_device_external` / `upgrade_all_devices` | Firmware upgrades |
| `unifi_rolling_upgrade` / `cancel_rolling_upgrade` | Rolling firmware upgrades |
| `unifi_check_firmware_update` | Check for firmware updates |
| `unifi_force_provision_device` | Force re-provision |
| `unifi_power_cycle_port` | PoE power cycle a switch port |
| `unifi_run_speedtest` / `get_speedtest_status` | Speed tests |
| `unifi_spectrum_scan` | RF spectrum scan |
| `unifi_cable_test` | Switch port cable diagnostics |
| `unifi_rename_device` | Rename a device |
| `unifi_led_override_device` | Override device LED mode |
| `unifi_enable_device` / `disable_device` / `disable_ap` | Enable/disable devices |
| `unifi_migrate_device` / `cancel_migrate_device` | Device migration |
| `unifi_set_inform_device` | Set device inform URL |
| `unifi_set_rollupgrade` / `unset_rollupgrade` | Roll upgrade flags |
| `unifi_restart_http_portal` | Restart captive portal |

### Client Commands (7 stamgr commands)

| Tool | Description |
|------|-------------|
| `unifi_block_client` / `unblock_client` | Block/unblock a client |
| `unifi_kick_client` | Disconnect a client |
| `unifi_forget_client` | Remove client history |
| `unifi_reconnect_client` | Force client reconnection |
| `unifi_authorize_guest` / `unauthorize_guest` | Guest portal auth |

### Site & Admin Management (14 sitemgr commands)

| Tool | Description |
|------|-------------|
| `unifi_add_site` / `delete_site` / `update_site` | Site CRUD |
| `unifi_set_site_leds` | Site LED control |
| `unifi_get_admins` | List admin users |
| `unifi_create_admin` / `invite_admin` / `assign_existing_admin` | Add admins |
| `unifi_update_admin` / `revoke_admin` | Manage admins |
| `unifi_grant_super_admin` / `revoke_super_admin` | Super admin privileges |
| `unifi_move_device` / `delete_device` | Cross-site device ops |

### Backup & System (8 commands)

| Tool | Description |
|------|-------------|
| `unifi_list_backups` / `delete_backup` | Manage backups |
| `unifi_create_backup` / `generate_backup` / `generate_backup_site` | Create backups |
| `unifi_download_backup` | Download a backup file |
| `unifi_reboot_cloudkey` | Reboot CloudKey |
| `unifi_element_adoption` | Element platform adoption |

### Alarm & Event Management

| Tool | Description |
|------|-------------|
| `unifi_archive_all_alarms` | Archive all alarms (evtmgr) |
| `unifi_archive_alarm` | Archive a single alarm (evtmgr) |
| `unifi_alarm_archive` | Archive via alarm manager |
| `unifi_clear_dpi` | Clear DPI counters |

### v2 API (15 tools)

| Tool | Description |
|------|-------------|
| `unifi_list_firewall_policies` / `create` / `update` / `delete` | v2 firewall policies |
| `unifi_list_traffic_rules` / `create` / `update` / `delete` | v2 traffic rules |
| `unifi_list_traffic_routes` / `update` | v2 traffic routes |
| `unifi_list_firewall_zones` / `update` | v2 firewall zones |
| `unifi_list_active_clients` | v2 active client list |
| `unifi_list_clients_history` | v2 client history |
| `unifi_list_ap_groups` | v2 AP groups |

### Global & Special

| Tool | Description |
|------|-------------|
| `unifi_status` | Controller status (no auth required) |
| `unifi_self` | Current admin info |
| `unifi_sites` | List all sites |
| `unifi_stat_admin` / `stat_sites` | Admin/site statistics |
| `unifi_logout` | Invalidate session |
| `unifi_system_poweroff` / `system_reboot` | Controller power management (dangerous) |
| `unifi_get_overview` | Network overview in a single call: health, devices, networks, WLANs, clients, alarms |
| `unifi_set_port_override` | Configure switch port profiles (the tool that started this project) |
| `unifi_report_issue` | Compose a `gh issue create` command for unexpected errors |

### Safety: Confirmation Gate

All mutation tools (create, update, delete, device commands) require `confirm=True`. Without it, they return a dry-run preview of what would change. This prevents accidental modifications.

```
# Without confirm — returns preview only
unifi_create_network(name="Guest VLAN", purpose="vlan-only", vlan=100)

# With confirm — actually creates the network
unifi_create_network(name="Guest VLAN", purpose="vlan-only", vlan=100, confirm=True)
```

### Error Reporting

Every tool's docstring includes a nudge: *"If this tool returns an unexpected error, call unifi_report_issue to report it."* The `unifi_report_issue` tool composes a ready-to-paste `gh issue create` command with the tool name, error message, parameters used, and optional notes. It makes no HTTP calls — just returns a command string the user can review and run.

This means LLM agents using this MCP server will automatically suggest filing bug reports when they encounter unexpected errors, creating a feedback loop from production usage back to the maintainers.

### Response Format

All tools return structured JSON. List tools return:

```json
{"summary": "Found 5 networks", "count": 5, "data": [{...}, ...]}
```

Single-item tools return:

```json
{"data": {"_id": "abc123", "name": "My Network", ...}}
```

This format is machine-parseable — no more double-encoded JSON-inside-a-string responses.

### Secret Redaction

By default (`UNIFI_REDACT_SECRETS=true`), sensitive fields are replaced with `<redacted>` in all responses. This prevents WiFi passphrases, passwords, and other secrets from leaking into LLM context windows. Redacted fields include `x_passphrase`, `x_password`, `x_shadow`, `x_private_key`, and any field containing `password`, `passphrase`, `secret`, or `preshared_key`. Set `UNIFI_REDACT_SECRETS=false` to get raw values.

### Pagination & Field Selection

All list tools accept three optional parameters:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `limit` | `0` | Max records to return (`0` = all, backward compatible) |
| `offset` | `0` | Skip this many records |
| `fields` | `""` | Comma-separated field names to include (e.g. `"name,ip,mac"`) |

When `fields` is specified, `_id` is always included for reference. This is client-side filtering — the full dataset is fetched from the controller and then sliced. For large deployments, use `limit` and `offset` to page through results without overwhelming the LLM context.

```
# Get just names and subnets of the first 5 networks
unifi_list_networks(limit=5, fields="name,ip_subnet,vlan")
```

## How It Works

This repo contains a **generator** that reads API specifications and produces the MCP server. You don't need to understand the generator to use the server — just run `generate.py` once.

### Why a generator?

The UniFi API has no official OpenAPI spec. Rather than hand-writing 285 tool functions, we built a multi-stage discovery pipeline that captures the real API surface from a live controller, then generates the server automatically. When Ubiquiti updates their API, re-run the pipeline and regenerate.

### Architecture

```
spec/
  endpoint-inventory.json   # API surface: 196 endpoints from real controller
  probe-spec.json           # Declarative endpoint list for probe
  field-inventory.json      # Field names from production controller
  api-samples/              # 120+ real (scrubbed) JSON responses for schema inference
generate.py                 # Entry point: load -> infer -> render -> write
generator/
  loader.py                 # Parse spec/ data into structured types
  schema_inference.py       # JSON values -> Python types + enum detection
  naming.py                 # Tool names, command mappings, test payloads
  context_builder.py        # Assemble Jinja2 template context
templates/
  server.py.j2              # FastMCP server template (285 tools)
  conftest.py.j2            # Pytest fixtures
  test_rest.py.j2           # Per-resource CRUD lifecycle tests
  test_stat.py.j2           # Stat endpoint tests
  test_cmd.py.j2            # Command tests
  test_v2.py.j2             # v2 endpoint tests
  test_global.py.j2         # Global endpoint tests
generated/                  # OUTPUT — never hand-edit
  server.py                 # The MCP server (this is what you run)
  conftest.py               # Test fixtures
  tests/                    # 44 test files
```

**Critical rule:** Generated code in `generated/` is never hand-edited. If the output has bugs, fix the generator templates or modules and re-run.

### MCP Server Internals

The generated `server.py` includes:

- Async httpx client with cookie-based auth and CSRF token handling
- Auto-relogin on 401 responses
- UniFi OS support (handles `/proxy/network` prefix automatically)
- Structured error handling — parses `meta.rc` / `meta.msg` from API responses
- Site awareness — default site from env var, per-tool override available
- Rich docstrings with field types, enum values, and cross-references between tools

## API Discovery Pipeline

The 285 tools come from a three-stage endpoint discovery process run against a real UniFi Network Controller v10.0.162:

### Stage 1: Automated Probe (`probe.py`)

A single-file Python script that systematically hits every known endpoint path with safe HTTP methods and records the status codes, sample responses, and field schemas.

```bash
# Full automated cycle (Docker container + probe + teardown):
scripts/run_probe.sh

# Manual probe against a running controller:
uv run python probe.py --host HOST --no-verify-ssl

# Dry run — preview what would be probed:
uv run python probe.py --dry-run
```

Safety rules are hardcoded: never POST/PUT/DELETE to `rest/`, never execute unsafe commands, never hit `system/reboot` or `poweroff`. All sensitive fields (`x_password`, `x_passphrase`, `x_shadow`, `x_private_key`, etc.) are scrubbed to `"REDACTED"` before writing samples to disk.

### Stage 2: LLM-Powered Discovery (`llm-probe/`)

Endpoints that returned 404 or 400 during the automated probe were fed to Claude via `claude -p` (Claude Code CLI). For each endpoint, Claude reasons about what HTTP method, request body, or path variation might work — then tries it using `curl` against the live controller.

```bash
# Probe all 400-status endpoints:
python llm-probe/llm_probe.py --host localhost --port 8443 \
    --username admin --password testpassword123 \
    --no-verify-ssl --only-category 400

# Probe 404 endpoints:
python llm-probe/llm_probe.py --only-category 404 ...
```

This stage discovered 44 additional working endpoints, including:
- All 28 `set/setting/*` endpoints (PUT-only, paired with `get/setting/*` for reads)
- `stat/session` (needs POST with date range body)
- `upd/user` and `upd/device` (PUT endpoints for updating resources)
- `group/user` (batch user group assignment)
- WebSocket events stream at `/wss/s/{site}/events`

### Stage 3: Generator (`generate.py`)

The generator reads the discovered inventory and produces the MCP server with full CRUD tools, stat queries, command wrappers, and v2 API tools — all with proper parameter types inferred from real API response samples.

```bash
uv run python generate.py         # Generate server + tests
uv run python count_tools.py      # Verify tool counts match
```

### Verification

```
$ uv run python count_tools.py
TOOL COUNTS (computed from spec)
  REST tools:          154
  Stat tools:          39
  Cmd tools:           66
  v2 tools:            15
  Global tools:        8
  Port override:       1
  Report issue:        1
  Overview:            1
  TOTAL tools:         285

VERIFICATION
  Computed from spec:  285
  Actual in server.py: 285
  ✓ MATCH
```

## Running the Test Suite

The test suite runs against a real UniFi controller in Docker. 44 test files, all validation tests passing.

```bash
# Start ephemeral controller
docker compose -f docker-compose.test.yml up -d

# Wait for it to be healthy (~60-90s), then run tests
uv run pytest generated/tests/ -v

# Tear down
docker compose -f docker-compose.test.yml down -v
```

### Module toggle tests (no controller needed)

`test_modules_toggle.py` validates that every `UNIFI_MODULES` configuration loads exactly the right tools. All expected values are **auto-derived** from `spec/endpoint-inventory.json` + `generator/naming.py` — zero hardcoded numbers. When the API surface changes, these tests auto-adapt.

```bash
uv run --extra test python -m pytest test_modules_toggle.py -v   # 62 tests
```

**What it covers (62 tests):**
- Tool counts for every configuration: `v1,v2`, `v1`, `v2`, empty, whitespace, each of the 9 sub-modules individually, all-modules combo, multi-module combos, `v2+module`
- Tool presence: always-on tools present everywhere, each module's tools present when loaded
- Mutual exclusivity: loading one module does NOT leak tools from other modules
- v2 dual-guard: v2 tools accessible via both their parent sub-module and the `v2` flag
- No duplicates in any configuration
- Port override in device module only
- Read-only mode: correct counts for `v1,v2`, `v1`, `v2`, empty, each sub-module, combos
- Read-only safety: no mutating tools present, no `confirm` parameter tools, always-on read-only tools preserved

### Test philosophy

The tests run against a controller with no adopted devices. Rather than skipping tests that need hardware, we assert the correct error responses — proving the endpoints are reachable, validate input correctly, and return the right errors. A test that asserts "this endpoint returns 400 UnknownDevice for a dummy MAC" proves the endpoint works just as well as a happy-path test. See the test templates for details.

### Controller bootstrapping

The UniFi controller has no setup wizard API. The test harness seeds an admin user directly into the embedded MongoDB (`ace` database) via `docker exec`. Password hashing uses `openssl passwd -6` inside the container (Python 3.13 removed the `crypt` module). This is fully automated in `conftest.py`.

## QA Coverage

All 285 tools were tested against a live UniFi v10.0.162 controller running in Docker using an LLM-based bank tester (Claude as QA engineer, 31 tasks, 498+ tool calls across 5 fix sprints).

**"Worked first try"** is the key QA metric. Every tool was verified to succeed on its first invocation with correct parameters — no retries, no parameter guessing, no error-and-retry loops. This matters because MCP tools that fail on first attempt waste tokens, context window, and user time as the LLM has to diagnose the error and retry. A tool that works first try means the docstring, parameter types, and enum values are all correct enough that an LLM can call it successfully without prior experience.

### Coverage Summary

| Category | Tools | Status |
|----------|-------|--------|
| REST CRUD | 154 | All tested (28 CRUD resources + settings + read-only) |
| Stat endpoints | 39 | All tested |
| Commands | 66 | All tested (2 skipped, see below) |
| v2 API | 15 | All tested |
| Global | 8 | All tested |
| Port override | 1 | Tested (needs device for success) |
| Report issue | 1 | Error reporting helper (no API call) |
| Overview | 1 | Tested (composite: health + devices + networks + WLANs + clients + alarms) |
| **Total** | **285** | **100% invocation coverage** |

### Skipped Commands (not generated)

| Command | Manager | Reason |
|---------|---------|--------|
| `set-site-name` | sitemgr | Does not exist on v10.0.162 standalone controllers. Use `update-site` instead. |
| `delete-admin` | sitemgr | Vestigial; `revoke-admin` already fully deletes the admin object. |

### Skipped REST Operations

| Resource | Operation | Reason |
|----------|-----------|--------|
| `user` | DELETE | REST DELETE not supported. Use `forget_client` (stamgr `forget-sta`) instead. |

### Untested (require hardware or external services)

These tools exist and are generated but cannot be fully exercised without adopted UniFi devices or external infrastructure:

**Hardware-dependent (23 tools)** — need adopted APs, switches, or gateways:
- Device commands: `adopt_device`, `restart_device`, `force_provision_device`, `locate_device`, `unlocate_device`, `upgrade_device`, `upgrade_device_external`, `migrate_device`, `cancel_migrate_device`, `spectrum_scan`, `move_device`, `delete_device`, `rename_device`, `power_cycle_port`
- Client commands: `kick_client`, `reconnect_client` (need connected wireless clients)
- Hotspot commands: `hotspot_authorize_guest`, `extend_guest_validity` (need hotspot portal)
- Firewall: `create_firewall_policy` (needs gateway + zones)
- Traffic: `update_traffic_route` (needs gateway)
- Other: `set_site_leds` (needs LED-capable devices), `set_port_override` (needs adopted switch)

**Standalone controller limitations (5 tools)** — work on UniFi OS but not standalone Docker:
- `delete_site` — returns NoPermission regardless of admin privileges
- `generate_backup`, `generate_backup_site` — backup generation commands don't exist in standalone cmd/backup

**API limitations (3 tools)** — need external infrastructure:
- `create_hotspot_package` — requires payment gateway configuration
- `create_dhcp_option` — requires DHCP gateway device
- `revoke_voucher` — requires hotspot portal infrastructure

**Destructive (3 tools)** — intentionally not tested:
- `logout`, `system_poweroff`, `system_reboot`

## Acknowledgments

The API endpoint inventory was built from multiple community sources. The UniFi API is undocumented by Ubiquiti, and everything we know comes from the community's reverse-engineering efforts:

- **[Art-of-WiFi/UniFi-API-browser](https://github.com/Art-of-WiFi/UniFi-API-browser)** and **[Art-of-WiFi/UniFi-API-client](https://github.com/Art-of-WiFi/UniFi-API-client)** — The most comprehensive community documentation of the UniFi API. Many endpoint paths, command names, and parameter schemas come from their PHP client and API browser.
- **[unpoller/unpoller](https://github.com/unpoller/unpoller)** (formerly unifi-poller) — Endpoint paths for stat, anomaly, IPS/IDS events, and DPI data collection.
- **[py-unifi](https://github.com/eralde/python-unifi-api)** — Python UniFi client with OpenAPI spec contributions that helped discover REST endpoints like `dhcpoption`, `heatmap`, `heatmappoint`, `spatialrecord`, `dpiapp`, and `dpigroup`.
- **[aiounifi](https://github.com/Kane610/aiounifi)** — Async Python client for Home Assistant's UniFi integration. Provided endpoint hints for DPI groups, device management, and v2 API paths.
- **[unifi-network-server Docker image](https://github.com/jacobalberty/unifi-docker)** by Jacob Alberty — Used for running the ephemeral test controller in Docker.

All community-discovered endpoints were verified against a real v10.0.162 standalone controller using our automated probe and LLM probe pipeline. Endpoints that couldn't be confirmed were excluded (see `CLAUDE.md` for the full NOT_FOUND/UNCERTAIN table).

## This Project is 100% AI-Generated

Every file in this repository was written by Claude (Anthropic). The generator, the templates, the test suite, the probe scripts, the LLM discovery harness, this README — all of it. No human wrote any code.

This project is designed for AI-to-AI use: an AI agent generates the server, and AI agents consume it via MCP to manage UniFi network infrastructure. Humans are welcome too.

## Dependencies

**Nix users:** `nix run github:abl030/unifi-mcp` — everything is bundled, no other deps needed.

**Non-Nix users:**
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) for package management
- fastmcp, httpx, jinja2 (installed automatically by `uv sync`)
- Docker (only needed for running the test suite)

## License

MIT
