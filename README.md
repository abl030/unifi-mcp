# UniFi MCP Server

An MCP (Model Context Protocol) server that gives AI agents full control over Ubiquiti UniFi network infrastructure. 137 tools covering networks, firewall rules, switch ports, WiFi, clients, device commands, and more.

This entire project — the generator, the server, the test suite, and this README — was built by AI (Claude) and is designed to be installed and used by AI agents.

## Install This MCP Server

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- A UniFi Network Controller (standalone or UniFi OS)

### Step 1: Clone and generate

```bash
git clone https://github.com/YOUR_USER/unifi-mcp-generator.git
cd unifi-mcp-generator
uv sync
uv run python generate.py
```

This produces `generated/server.py` — the MCP server with 137 tools.

### Step 2: Configure your MCP client

Add this to your MCP client configuration:

**Claude Code** (`claude mcp add`):

```bash
claude mcp add unifi -- \
  env UNIFI_HOST=YOUR_CONTROLLER_IP \
  UNIFI_PORT=8443 \
  UNIFI_USERNAME=admin \
  UNIFI_PASSWORD=YOUR_PASSWORD \
  UNIFI_SITE=default \
  uv run --directory /path/to/unifi-mcp-generator fastmcp run generated/server.py
```

**Claude Desktop** (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "unifi": {
      "command": "uv",
      "args": [
        "run",
        "--directory", "/path/to/unifi-mcp-generator",
        "fastmcp", "run", "generated/server.py"
      ],
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

**Any MCP client** — the server command is:

```bash
uv run fastmcp run generated/server.py
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

## What You Get: 137 Tools

### Network Configuration (CRUD)

| Tool | Description |
|------|-------------|
| `unifi_list_networks` / `get` / `create` / `update` / `delete` | VLANs, subnets, DHCP |
| `unifi_list_firewall_rules` / `get` / `create` / `update` / `delete` | Firewall rules |
| `unifi_list_firewall_groups` / `get` / `create` / `update` / `delete` | IP/port groups |
| `unifi_list_port_forwards` / `get` / `create` / `update` / `delete` | Port forwarding |
| `unifi_list_port_profiles` / `get` / `create` / `update` / `delete` | Switch port profiles |
| `unifi_list_wlans` / `get` / `create` / `update` / `delete` | WiFi networks |
| `unifi_list_wlan_groups` / `get` / `create` / `update` / `delete` | WLAN groups |
| `unifi_list_routes` / `get` / `create` / `update` / `delete` | Static routes |
| `unifi_list_dynamic_dns_entries` / `get` / `create` / `update` / `delete` | Dynamic DNS |
| `unifi_list_radius_profiles` / `get` / `create` / `update` / `delete` | RADIUS profiles |
| `unifi_list_user_groups` / `get` / `create` / `update` / `delete` | User groups |
| `unifi_list_tags` / `get` / `create` / `update` / `delete` | Tags |
| `unifi_list_accounts` / `get` / `create` / `update` / `delete` | RADIUS accounts |
| `unifi_list_users` / `get` / `create` / `update` / `delete` | Known clients |

### Settings, Alarms, Events (Read / Read-only)

| Tool | Description |
|------|-------------|
| `unifi_list_settings` / `get_setting` / `update_setting` | Site settings (38 categories) |
| `unifi_list_alarms` | Alarm history |
| `unifi_list_events` | Event log |

### Device Monitoring (stat endpoints)

| Tool | Description |
|------|-------------|
| `unifi_list_devices` | All adopted devices with full details |
| `unifi_list_clients` | Connected clients (IP, MAC, signal, traffic) |
| `unifi_list_health` | Network health subsystems |
| `unifi_list_rogue_aps` | Detected rogue access points |
| `unifi_list_sessions` | Client sessions |
| `unifi_list_sysinfo` | System information |
| `unifi_list_devices_basic` | Devices (basic info) |
| `unifi_list_stat_alarms` / `stat_events` | Stat-level alarm/event data |
| `unifi_list_site_dpi` / `client_dpi` | DPI (deep packet inspection) stats |
| `unifi_list_country_codes` / `current_channels` / `routing_stats` / `authorizations` | Misc stats |
| `unifi_list_dynamic_dns_stats` / `port_forward_stats` | Service stats |
| `unifi_list_report` | Hourly/daily/monthly reports |

### Device Commands

| Tool | Description |
|------|-------------|
| `unifi_restart_device` | Restart a device |
| `unifi_adopt_device` | Adopt a new device |
| `unifi_locate_device` / `unlocate_device` | Flash device LEDs |
| `unifi_upgrade_device` / `upgrade_device_external` | Firmware upgrade |
| `unifi_force_provision_device` | Force re-provision |
| `unifi_power_cycle_port` | PoE power cycle a switch port |
| `unifi_run_speedtest` / `get_speedtest_status` | Speed test |
| `unifi_spectrum_scan` | RF spectrum scan |
| `unifi_migrate_device` / `cancel_migrate_device` | Device migration |

### Client Commands

| Tool | Description |
|------|-------------|
| `unifi_block_client` / `unblock_client` | Block/unblock a client |
| `unifi_kick_client` | Disconnect a client |
| `unifi_forget_client` | Remove client history |
| `unifi_authorize_guest` / `unauthorize_guest` | Guest portal auth |

### Site & System

| Tool | Description |
|------|-------------|
| `unifi_add_site` / `delete_site` / `update_site` | Site management |
| `unifi_get_admins` | List admin users |
| `unifi_move_device` / `delete_device` | Cross-site device ops |
| `unifi_list_backups` / `delete_backup` / `create_backup` | Backup management |
| `unifi_archive_all_alarms` | Archive all alarms |
| `unifi_clear_dpi` | Clear DPI counters |

### v2 API

| Tool | Description |
|------|-------------|
| `unifi_list_firewall_policies` / `create` / `update` / `delete` | v2 firewall policies |
| `unifi_list_traffic_rules` / `create` / `update` / `delete` | v2 traffic rules |

### Global & Special

| Tool | Description |
|------|-------------|
| `unifi_status` | Controller status (no auth required) |
| `unifi_self` | Current admin info |
| `unifi_sites` | List all sites |
| `unifi_stat_admin` / `stat_sites` | Admin/site statistics |
| `unifi_set_port_override` | Configure switch port profiles (the tool that started this project) |

### Safety: Confirmation Gate

All mutation tools (create, update, delete, device commands) require `confirm=True`. Without it, they return a dry-run preview of what would change. This prevents accidental modifications.

```
# Without confirm — returns preview only
unifi_create_network(name="Guest VLAN", purpose="vlan-only", vlan=100)

# With confirm — actually creates the network
unifi_create_network(name="Guest VLAN", purpose="vlan-only", vlan=100, confirm=True)
```

## How It Works

This repo contains a **generator** that reads API specifications and produces the MCP server. You don't need to understand the generator to use the server — just run `generate.py` once.

### Why a generator?

The UniFi API has 137 endpoints with no official OpenAPI spec. Rather than hand-writing 137 tool functions, we captured real API responses from a v10.0.162 controller and wrote a generator that produces the server automatically. When Ubiquiti updates their API, re-capture samples and re-run the generator.

### Architecture

```
endpoint-inventory.json     # API surface captured from real controller
api-samples/                # Real (scrubbed) JSON responses for schema inference
generate.py                 # Entry point: load → infer → render → write
generator/
  loader.py                 # Parse inventory + samples
  schema_inference.py       # JSON values → Python types
  naming.py                 # Tool names, command mappings, test payloads
  context_builder.py        # Assemble Jinja2 template context
templates/
  server.py.j2              # FastMCP server template (137 tools)
  conftest.py.j2            # Pytest fixtures
  test_rest.py.j2           # Per-resource CRUD lifecycle tests
  test_stat.py.j2           # Stat endpoint tests
  test_cmd.py.j2            # Command tests
  test_v2.py.j2             # v2 endpoint tests
  test_global.py.j2         # Global endpoint tests
generated/                  # OUTPUT — never hand-edit
  server.py                 # The MCP server (this is what you run)
  conftest.py               # Test fixtures
  tests/                    # 21 test files, 69 integration tests
```

**Critical rule:** Generated code in `generated/` is never hand-edited. If the output has bugs, fix the generator templates or modules and re-run.

### MCP Server Internals

The generated `server.py` includes:

- Async httpx client with cookie-based auth and CSRF token handling
- Auto-relogin on 401 responses
- UniFi OS support (handles `/proxy/network` prefix automatically)
- Structured error handling — parses `meta.rc` / `meta.msg` from API responses
- Site awareness — default site from env var, per-tool override available

## Running the Test Suite

The test suite runs against a real UniFi controller in Docker. 69 tests, all passing.

```bash
# Start ephemeral controller
docker compose -f docker-compose.test.yml up -d

# Wait for it to be healthy (~60-90s), then run tests
uv run pytest generated/tests/ -v

# Tear down
docker compose -f docker-compose.test.yml down -v
```

### Test philosophy

The tests run against a controller with no adopted devices. Rather than skipping tests that need hardware, we assert the correct error responses — proving the endpoints are reachable, validate input correctly, and return the right errors. A test that asserts "this endpoint returns 400 UnknownDevice for a dummy MAC" proves the endpoint works just as well as a happy-path test. See the test templates for details.

### Controller bootstrapping

The UniFi controller has no setup wizard API. The test harness seeds an admin user directly into the embedded MongoDB (`ace` database) via `docker exec`. Password hashing uses `openssl passwd -6` inside the container (Python 3.13 removed the `crypt` module). This is fully automated in `conftest.py`.

## This Project is 100% AI-Generated

Every file in this repository was written by Claude (Anthropic). The generator, the templates, the test suite, the Docker harness, this README — all of it. No human wrote any code.

This project is designed for AI-to-AI use: an AI agent generates the server, and AI agents consume it via MCP to manage UniFi network infrastructure. Humans are welcome too.

## Dependencies

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) for package management
- fastmcp, httpx, jinja2 (installed automatically by `uv sync`)
- Docker (only needed for running the test suite)

## License

MIT
