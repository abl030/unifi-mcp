# Bank Tester Results Summary

**Results directory**: `bank-tester/results/run-20260210-130113`

**Tasks analyzed**: 1

## Overall Status

- **success**: 1

**Total tool calls**: 7
**First-attempt failures**: 1
**First-attempt success rate**: 85.7%

## Failure Categories

| Category | Count |
|----------|-------|
| `missing_required_field` | 1 |

## Tools With Most Failures

| Tool | Failures |
|------|----------|
| `unifi_create_spatial_record` | 1 |

## Per-Task Results

### 32-verify-spatialrecord-fix

- **Status**: success
- **Tool calls**: 7
- **First-attempt failures**: 1
- **Cleanup complete**: true
- **Failure details**:
  - `unifi_create_spatial_record` [missing_required_field]: The minimal data (only name + devices) caused the API to return empty array. Adding a description field resulted in proper response with _id.
- **Notes**: The spatial record fix (devices: []) works correctly. However, discovered that the API requires at least one additional field beyond name + devices to return the created object. When only name + devices are provided, the API returns an empty array, making it impossible to retrieve the _id for subsequent operations.
  
  The generator should update the docstring for create_spatial_record to indicate that while name and devices are the technical minimum, including additional fields (like description) is recommended to receive the created object in the response.
  
  Full CRUD lifecycle (create, list, get, update, delete, verify deletion) all worked correctly once a description field was added.

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
  - ... and 231 more

## Actionable Findings

- **Required fields**: Generator should mark required fields more clearly
