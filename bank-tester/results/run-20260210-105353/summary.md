# Bank Tester Results Summary

**Results directory**: `bank-tester/results/run-20260210-105353`

**Tasks analyzed**: 1

## Overall Status

- **success**: 1

**Total tool calls**: 12
**First-attempt failures**: 0
**First-attempt success rate**: 100.0%

## Per-Task Results

### 02-network-and-user-group-crud

- **Status**: success
- **Tool calls**: 12
- **First-attempt failures**: 0
- **Cleanup complete**: true
- **Notes**: All 10 tools exercised successfully with no failures. The MCP server returned JSON strings in the "result" field rather than parsed objects, but this did not cause any operational issues. All CRUD operations (create, list, get, update, delete) worked as expected for both networks and user groups.
  
  Network operations tested:
  - Created VLAN-only network with vlan=999
  - Listed and verified presence in results
  - Retrieved by ID successfully
  - Updated name field and verified change persisted
  - Deleted successfully
  
  User group operations tested:
  - Created user group with minimal config (name only)
  - Listed and verified presence in results
  - Retrieved by ID successfully
  - Updated name field and verified change persisted
  - Deleted successfully
  
  The confirm=True parameter worked correctly as a safety gate for all mutation operations.

## Tool Coverage

- **Total tools**: 286
- **Tools invoked**: 11
- **Coverage**: 3.8%
- **Not covered** (275):
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
  - `unifi_create_voucher`
  - `unifi_create_wlan`
  - `unifi_create_wlan_group`
  - `unifi_delete_account`
  - `unifi_delete_admin`
  - `unifi_delete_backup`
  - `unifi_delete_broadcast_group`
  - ... and 225 more
