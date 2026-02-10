# Bank Tester Results Summary

**Results directory**: `bank-tester/results/run-20260210-105234`

**Tasks analyzed**: 1

## Overall Status

- **success**: 1

**Total tool calls**: 6
**First-attempt failures**: 4
**First-attempt success rate**: 33.3%

## Failure Categories

| Category | Count |
|----------|-------|
| `unexpected_error` | 4 |

## Tools With Most Failures

| Tool | Failures |
|------|----------|
| `unifi_self` | 1 |
| `unifi_sites` | 1 |
| `unifi_stat_sites` | 1 |
| `unifi_stat_admin` | 1 |

## Per-Task Results

### 01-global-endpoints

- **Status**: success
- **Tool calls**: 6
- **First-attempt failures**: 4
- **Cleanup complete**: true
- **Failure details**:
  - `unifi_self` [unexpected_error]: Controller was still starting up (status showed "up": false), authentication endpoint not yet ready
  - `unifi_sites` [unexpected_error]: Controller was still starting up, cascading failure from unifi_self error
  - `unifi_stat_sites` [unexpected_error]: Controller was still starting up, cascading failure from unifi_self error
  - `unifi_stat_admin` [unexpected_error]: Controller was still starting up, cascading failure from unifi_self error
- **Notes**: All 5 global endpoint tools exercised successfully after controller startup delay.
  
  Friction points:
  1. **Startup race condition**: When testing immediately after container start, the controller returns "up": false in the status endpoint, but authenticated endpoints fail with JSON parsing errors. The status endpoint works before authentication is ready, creating a false positive for "controller ready" state.
  
  2. **Error message quality**: The "Expecting value: line 1 column 1 (char 0)" error suggests the server returned empty response or HTML instead of JSON, but this wasn't surfaced to the user. A clearer error like "Controller returned non-JSON response (may still be starting)" would be more helpful.
  
  3. **Tool discoverability**: All tool names were intuitive and matched the task description exactly. The `unifi_` prefix made searching straightforward.
  
  4. **Docstring quality**: The status tool correctly noted "No authentication required" but other tools had minimal descriptions ("Self.", "Sites."). More context about what each endpoint returns would be helpful (e.g., "Returns current authenticated admin user details" for unifi_self).
  
  5. **No parameters needed**: All global tools correctly require no parameters, making them very easy to use.
  
  Recommendation: The bank tester harness should wait for both `"up": true` in status AND successful authentication (e.g., call unifi_self) before declaring the controller ready for testing.

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

