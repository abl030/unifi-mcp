# Bank Tester Results Summary

**Results directory**: `bank-tester/results/run-20260210-105521`

**Tasks analyzed**: 1

## Overall Status

- **success**: 1

**Total tool calls**: 12
**First-attempt failures**: 0
**First-attempt success rate**: 100.0%

## Per-Task Results

### 03-firewall-groups-and-rules-crud

- **Status**: success
- **Tool calls**: 12
- **First-attempt failures**: 0
- **Cleanup complete**: true
- **Notes**: All 10 firewall group and rule tools worked flawlessly on first attempt. Tool naming was intuitive and parameter requirements were clear from docstrings. The confirm=True gate pattern worked as expected for all mutations. Cross-references in docstrings (e.g., "Reference this group's _id in src_firewallgroup_ids") were helpful but not needed for basic CRUD operations. All operations returned properly structured JSON with clear success indicators.

## Tool Coverage

- **Total tools**: 286
- **Tools invoked**: 10
- **Coverage**: 3.5%
- **Not covered** (276):
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
  - `unifi_create_firewall_policy`
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
  - ... and 226 more
