# Bank Tester Results Summary

**Results directory**: `bank-tester/results/run-20260210-105651`

**Tasks analyzed**: 1

## Overall Status

- **partial**: 1

**Total tool calls**: 8
**First-attempt failures**: 1
**First-attempt success rate**: 87.5%

## Failure Categories

| Category | Count |
|----------|-------|
| `unexpected_error` | 1 |

## Tools With Most Failures

| Tool | Failures |
|------|----------|
| `mcp__unifi__unifi_clear_dpi` | 1 |

## Per-Task Results

### 08-safe-commands

- **Status**: partial
- **Tool calls**: 8
- **First-attempt failures**: 1
- **Cleanup complete**: true
- **Failure details**:
  - `mcp__unifi__unifi_clear_dpi` [unexpected_error]: The clear-dpi command is routed to /cmd/stat which returns 404. This appears to be a generator issue - the command may be mapped to the wrong endpoint or the endpoint doesn't exist in this controller version.
- **Notes**: 6 out of 7 tools worked successfully. The unifi_clear_dpi tool failed with a 404 error at /api/s/default/cmd/stat, suggesting either:
  1. The command is mapped to the wrong manager in the generator (should be cmd/stamgr or similar, not cmd/stat)
  2. The clear-dpi command doesn't exist on this controller version
  3. The endpoint requires specific preconditions not met
  
  All other command tools executed successfully and returned empty arrays (expected for a fresh controller with no speedtests, no firmware updates pending, no backups, etc.).
  
  Initial parallel execution failed with "Expecting value: line 1 column 1 (char 0)" - this appears to be a transient error or parallel execution issue with the MCP server, as sequential retries succeeded.

## Tool Coverage

- **Total tools**: 286
- **Tools invoked**: 7
- **Coverage**: 2.4%
- **Not covered** (279):
  - `unifi_add_site`
  - `unifi_adopt_device`
  - `unifi_advanced_adopt_device`
  - `unifi_alarm_archive`
  - `unifi_archive_alarm`
  - `unifi_assign_existing_admin`
  - `unifi_authorize_guest`
  - `unifi_block_client`
  - `unifi_cable_test`
  - `unifi_cancel_migrate_device`
  - `unifi_cancel_rolling_upgrade`
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
  - `unifi_delete_backup`
  - `unifi_delete_broadcast_group`
  - `unifi_delete_device`
  - ... and 229 more

## Actionable Findings

