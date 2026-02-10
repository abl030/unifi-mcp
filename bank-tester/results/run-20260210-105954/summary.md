# Bank Tester Results Summary

**Results directory**: `bank-tester/results/run-20260210-105954`

**Tasks analyzed**: 1

## Overall Status

- **partial**: 1

**Total tool calls**: 10
**First-attempt failures**: 2
**First-attempt success rate**: 80.0%

## Failure Categories

| Category | Count |
|----------|-------|
| `hardware_dependent` | 3 |
| `unexpected_error` | 1 |

## Tools With Most Failures

| Tool | Failures |
|------|----------|
| `unifi_create_firewall_policy` | 3 |
| `unifi_list_firewall_policies` | 1 |

## Per-Task Results

### 16-v2-firewall-policies-and-zones

- **Status**: partial
- **Tool calls**: 10
- **First-attempt failures**: 2
- **Cleanup complete**: true
- **Failure details**:
  - `unifi_list_firewall_policies` [unexpected_error]: Initial call failed with JSON parsing error, but subsequent call worked. May be a transient server startup issue or race condition.
  - `unifi_create_firewall_policy` [hardware_dependent]: All create attempts failed with 400 regardless of payload structure (tried minimal name-only, name+enabled, and name+enabled+action+matching). The v2 firewall policies API may require specific prerequisites (firewall rules, zones configuration, or hardware) that are not present in a bare controller setup.
  - `unifi_create_firewall_policy` [hardware_dependent]: Same 400 error with more complete payload
  - `unifi_create_firewall_policy` [hardware_dependent]: Same 400 error with minimal payload. This endpoint is not functional without additional prerequisites.
- **Notes**: The v2 firewall policies API appears to require prerequisites not present in a bare controller:
  - list_firewall_policies works (returns empty list)
  - list_firewall_zones works (returns empty list)
  - create_firewall_policy fails with 400 regardless of payload
  - Initial list_firewall_policies call failed with JSON parse error but retry succeeded (transient issue)
  
  Tool discoverability: Good. All tools were easy to find and had clear names.
  Docstrings: Adequate but could benefit from:
    - Example payload structures for create/update operations
    - Prerequisites or dependencies (e.g., "requires firewall rules" or "requires adopted gateway")
    - Common error scenarios (400 = missing prerequisites vs bad payload)
  
  The confirm=True workflow worked correctly (dry-run preview, then execute).
  
  Since create/update/delete are blocked by the 400 error, I was unable to test:
  - unifi_update_firewall_policy
  - unifi_delete_firewall_policy
  - unifi_update_firewall_zone (no zones exist to update)
  
  Successfully tested:
  - unifi_list_firewall_policies (2 calls, 1 success after retry)
  - unifi_list_firewall_zones (1 call, success)
  - unifi_create_firewall_policy (4 calls including preview, all failed with 400)

## Tool Coverage

- **Total tools**: 286
- **Tools invoked**: 3
- **Coverage**: 1.0%
- **Not covered** (283):
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
  - ... and 233 more

## Actionable Findings

- **Hardware-dependent**: These tools require adopted devices — consider mock device seeding
