# Bank Tester Results Summary

**Results directory**: `bank-tester/results/run-20260210-125339`

**Tasks analyzed**: 1

## Overall Status

- **partial**: 1

**Total tool calls**: 30
**First-attempt failures**: 3
**First-attempt success rate**: 90.0%

## Failure Categories

| Category | Count |
|----------|-------|
| `missing_required_field` | 3 |

## Tools With Most Failures

| Tool | Failures |
|------|----------|
| `unifi_create_hotspot_package` | 1 |
| `unifi_create_dhcp_option` | 1 |
| `unifi_create_spatial_record` | 1 |

## Per-Task Results

### 31-verify-generator-fixes

- **Status**: partial
- **Tool calls**: 30
- **First-attempt failures**: 3
- **Cleanup complete**: true
- **Failure details**:
  - `unifi_create_hotspot_package` [missing_required_field]: The documented required fields (name, amount, currency, duration, bytes) are incomplete. The UniFi API requires additional undocumented fields that are not present in the sample data or tool docstring.
  - `unifi_create_dhcp_option` [missing_required_field]: The documented required fields (name, code, value) are incomplete. The UniFi API requires additional undocumented fields that are not present in the sample data or tool docstring.
  - `unifi_create_spatial_record` [missing_required_field]: The documented required fields (name, map_id, x, y, z) are present but the API still rejects the payload with api.err.Invalid. Either the field types are wrong or additional validation rules exist that are not documented.
- **Notes**: SUCCESSES (18/21 previously-failing calls now work):
  
  Section A: Settings Update (6 calls, 6 succeeded)
  - unifi_update_setting with key=ntp: SUCCESS (previously failed)
  - unifi_update_setting with key=connectivity: SUCCESS (previously failed)
  - unifi_update_setting with key=mgmt: SUCCESS (previously failed)
  - unifi_update_setting with key=guest_access: SUCCESS (previously failed)
  - All settings updates now use correct set/setting/{key} endpoint
  
  Section B: Sessions Stat (1 call, 1 succeeded)
  - unifi_list_sessions: SUCCESS (previously failed with api.err.InvalidArgs)
  - Tool now includes built-in POST body {"type":"all","start":0,"end":9999999999}
  
  Section C: Undocumented Resource Creates (5 calls, 2 succeeded, 3 failed)
  - unifi_create_map: SUCCESS
  - unifi_create_heatmap: SUCCESS (previously undocumented, now documented with required fields)
  - unifi_create_heatmap_point: SUCCESS (previously undocumented, now documented with required fields)
  - unifi_create_hotspot_package: FAILED (documented fields incomplete)
  - unifi_create_dhcp_option: FAILED (documented fields incomplete)
  - unifi_create_spatial_record: FAILED (documented fields present but still rejected)
  
  Section D: Full-Object Update Pattern (2 calls, 2 succeeded)
  - unifi_update_schedule_task: SUCCESS (previously failed, now has docstring note about full object requirement)
  - unifi_update_traffic_rule: SUCCESS (previously failed, now has docstring note about full object requirement)
  
  Section E: DPI Reset (1 call, 1 succeeded)
  - unifi_clear_dpi: SUCCESS (previously 404, now correctly mapped to reset-dpi command)
  
  Section F: MAC Validation (1 call, 1 succeeded)
  - unifi_block_client with bad MAC: SUCCESS (client-side validation now catches format errors before API call)
  
  REMAINING FAILURES (3/21):
  All 3 failures are due to incomplete required field documentation. The generator correctly inferred fields from sample data, but the samples may be incomplete or the API has undocumented validation requirements.
  
  GENERATOR FIXES VERIFIED:
  1. Settings endpoint routing (set/setting/{key}) - FIXED ✓
  2. stat/session POST body defaults - FIXED ✓
  3. Heatmap/heatmap_point required fields - FIXED ✓
  4. Schedule task full-object docstring - FIXED ✓
  5. Traffic rule full-object docstring - FIXED ✓
  6. Traffic rule enum values - FIXED ✓
  7. clear_dpi command mapping - FIXED ✓
  8. MAC address client-side validation - FIXED ✓
  
  Overall: 85.7% success rate (18/21 previously-failing calls now succeed)

## Tool Coverage

- **Total tools**: 286
- **Tools invoked**: 23
- **Coverage**: 8.0%
- **Not covered** (263):
  - `unifi_add_site`
  - `unifi_adopt_device`
  - `unifi_advanced_adopt_device`
  - `unifi_alarm_archive`
  - `unifi_archive_alarm`
  - `unifi_archive_all_alarms`
  - `unifi_assign_existing_admin`
  - `unifi_authorize_guest`
  - `unifi_cable_test`
  - `unifi_cancel_migrate_device`
  - `unifi_cancel_rolling_upgrade`
  - `unifi_check_firmware_update`
  - `unifi_create_account`
  - `unifi_create_admin`
  - `unifi_create_backup`
  - `unifi_create_broadcast_group`
  - `unifi_create_dns_record`
  - `unifi_create_dpi_app`
  - `unifi_create_dpi_group`
  - `unifi_create_dynamic_dns`
  - `unifi_create_firewall_group`
  - `unifi_create_firewall_policy`
  - `unifi_create_firewall_rule`
  - `unifi_create_hotspot2_config`
  - `unifi_create_hotspot_operator`
  - `unifi_create_media_file`
  - `unifi_create_network`
  - `unifi_create_port_forward`
  - `unifi_create_port_profile`
  - `unifi_create_radius_account`
  - `unifi_create_radius_profile`
  - `unifi_create_route`
  - `unifi_create_tag`
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
  - `unifi_delete_dhcp_option`
  - `unifi_delete_dns_record`
  - `unifi_delete_dpi_app`
  - `unifi_delete_dpi_group`
  - `unifi_delete_dynamic_dns`
  - `unifi_delete_firewall_group`
  - `unifi_delete_firewall_policy`
  - ... and 213 more

## Actionable Findings

- **Required fields**: Generator should mark required fields more clearly
