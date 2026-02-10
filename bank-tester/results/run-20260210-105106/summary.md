# Bank Tester Results Summary

**Results directory**: `bank-tester/results/run-20260210-105106`

**Tasks analyzed**: 1

## Overall Status

- **failed**: 1

**Total tool calls**: 10
**First-attempt failures**: 5
**First-attempt success rate**: 50.0%

## Failure Categories

| Category | Count |
|----------|-------|
| `unexpected_error` | 5 |

## Tools With Most Failures

| Tool | Failures |
|------|----------|
| `mcp__unifi__unifi_status` | 1 |
| `mcp__unifi__unifi_self` | 1 |
| `mcp__unifi__unifi_sites` | 1 |
| `mcp__unifi__unifi_stat_sites` | 1 |
| `mcp__unifi__unifi_stat_admin` | 1 |

## Per-Task Results

### 01-global-endpoints

- **Status**: failed
- **Tool calls**: 10
- **First-attempt failures**: 5
- **Cleanup complete**: true
- **Failure details**:
  - `mcp__unifi__unifi_status` [unexpected_error]: "DNS resolution failure - the MCP server's UNIFI_HOST environment variable is not pointing to a reachable controller. This is an infrastructure issue, not a tool design problem."
  - `mcp__unifi__unifi_self` [unexpected_error]: "Same DNS resolution failure - controller host not configured or unreachable."
  - `mcp__unifi__unifi_sites` [unexpected_error]: "Same DNS resolution failure - controller host not configured or unreachable."
  - `mcp__unifi__unifi_stat_sites` [unexpected_error]: "Same DNS resolution failure - controller host not configured or unreachable."
  - `mcp__unifi__unifi_stat_admin` [unexpected_error]: "Same DNS resolution failure - controller host not configured or unreachable."
- **Notes**: Infrastructure failure: All 5 global endpoint tools failed with "[Errno -2] Name or service not known", indicating the UniFi controller is not reachable at the configured hostname. This is not a tool design issue but rather an environment configuration problem.
  
  The MCP server likely needs UNIFI_HOST, UNIFI_USERNAME, UNIFI_PASSWORD, and other environment variables to be set to point to a running UniFi controller instance.
  
  Tool discoverability observations:
  - All 5 tools were easily found using ToolSearch with exact names
  - Tool names follow clear pattern: unifi_{endpoint_name}
  - No parameters required for these global endpoints (as expected)
  - Docstrings are minimal but sufficient for these simple read-only endpoints
  - unifi_status docstring helpfully notes "No authentication required"
  
  Cannot assess actual API behavior or response structure quality without a working controller connection.

## Tool Coverage

- **Total tools**: 286
- **Tools invoked**: 5
- **Coverage**: 1.7%
- **Not covered** (281):
  - `unifi_add_site`
  - `unifi_adopt_device`
  - `unifi_advanced_adopt_device`
  - `unifi_alarm_archive`
  - `unifi_archive_alarm`
  - `unifi_archive_all_alarms`
  - `unifi_assign_existing_admin`
  - `unifi_authorize_guest`
  - `unifi_block_client`
  - `unifi_cable_test`
  - `unifi_cancel_migrate_device`
  - `unifi_cancel_rolling_upgrade`
  - `unifi_check_firmware_update`
  - `unifi_clear_dpi`
  - `unifi_create_account`
  - `unifi_create_admin`
  - `unifi_create_backup`
  - `unifi_create_broadcast_group`
  - `unifi_create_dhcp_option`
  - `unifi_create_dns_record`
  - `unifi_create_dpi_app`
  - `unifi_create_dpi_group`
  - `unifi_create_dynamic_dns`
  - `unifi_create_firewall_group`
  - `unifi_create_firewall_policy`
  - `unifi_create_firewall_rule`
  - `unifi_create_heatmap`
  - `unifi_create_heatmap_point`
  - `unifi_create_hotspot2_config`
  - `unifi_create_hotspot_operator`
  - `unifi_create_hotspot_package`
  - `unifi_create_map`
  - `unifi_create_media_file`
  - `unifi_create_network`
  - `unifi_create_port_forward`
  - `unifi_create_port_profile`
  - `unifi_create_radius_account`
  - `unifi_create_radius_profile`
  - `unifi_create_route`
  - `unifi_create_schedule_task`
  - `unifi_create_spatial_record`
  - `unifi_create_tag`
  - `unifi_create_traffic_rule`
  - `unifi_create_user`
  - `unifi_create_user_group`
  - `unifi_create_voucher`
  - `unifi_create_wlan`
  - `unifi_create_wlan_group`
  - `unifi_delete_account`
  - `unifi_delete_admin`
  - ... and 231 more

## Actionable Findings

