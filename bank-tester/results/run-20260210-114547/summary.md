# Bank Tester Results Summary

**Results directory**: `bank-tester/results/run-20260210-114547`

**Tasks analyzed**: 1

## Overall Status

- **partial**: 1

**Total tool calls**: 10
**First-attempt failures**: 8
**First-attempt success rate**: 20.0%

## Failure Categories

| Category | Count |
|----------|-------|
| `error_quality_missing` | 4 |
| `error_quality_clear` | 3 |
| `error_quality_unclear` | 2 |
| `missing_required_field` | 1 |

## Tools With Most Failures

| Tool | Failures |
|------|----------|
| `unifi_create_network` | 2 |
| `unifi_update_network` | 1 |
| `unifi_delete_network` | 1 |
| `unifi_get_setting` | 1 |
| `unifi_update_setting` | 1 |
| `unifi_block_client` | 1 |
| `unifi_create_firewall_rule` | 1 |
| `unifi_create_port_forward` | 1 |
| `unifi_status` | 1 |

## Per-Task Results

### 30-adversarial

- **Status**: partial
- **Tool calls**: 10
- **First-attempt failures**: 8
- **Cleanup complete**: true
- **Failure details**:
  - `unifi_create_network` [error_quality_missing]: The error code "api.err.VlanUsed" is cryptic and doesn't explain what's wrong. The real issue is the missing 'name' field, but the error message talks about VLAN being used, which is misleading.
  - `unifi_create_network` [error_quality_missing]: Generic "InvalidPayload" error doesn't specify which field is invalid or what values are acceptable. No mention of valid purpose values.
  - `unifi_update_network` [error_quality_unclear]: "api.err.IdInvalid" explains the ID is invalid but doesn't say if it's malformed, non-existent, or wrong format. Better than nothing but not actionable.
  - `unifi_delete_network` [error_quality_unclear]: Same as update_network - "api.err.IdInvalid" is unclear whether the issue is formatting or existence.
  - `unifi_get_setting` [error_quality_clear]: Clear error message that explicitly states the setting was not found. This is good error handling.
  - `unifi_update_setting` [error_quality_clear]: Excellent client-side validation error from Pydantic. Clearly states expected type (dictionary) and what was received (string). Includes validation URL.
  - `unifi_block_client` [missing_required_field]: CRITICAL BUG - The API accepted an invalid MAC address format ("not-a-mac") and created a blocked client record with this malformed MAC. No validation occurred at either client or server side. This should have failed.
  - `unifi_create_firewall_rule` [error_quality_missing]: Error code indicates fields are required but doesn't specify which ones. Generic error - not helpful for knowing what to add.
  - `unifi_create_port_forward` [error_quality_missing]: Generic "InvalidPayload" doesn't specify if the issue is the out-of-range port numbers (99999, -1) or something else. No actionable information.
  - `unifi_status` [error_quality_clear]: Successfully returned controller status as expected. No errors.
- **Notes**: **Error Message Quality Summary**:
  
  CLEAR (2/10):
  - unifi_get_setting: Explicit "Setting 'X' not found" message
  - unifi_update_setting: Pydantic validation with type details and reference URL
  - unifi_status: Success case
  
  UNCLEAR (2/10):
  - unifi_update_network: "api.err.IdInvalid" indicates problem but not specific cause
  - unifi_delete_network: Same issue - unclear if ID is malformed or non-existent
  
  MISSING (5/10):
  - unifi_create_network (missing name): Misleading "api.err.VlanUsed" instead of "name required"
  - unifi_create_network (bad enum): Generic "InvalidPayload" without field or valid values
  - unifi_create_firewall_rule: "FirewallRuleFieldsRequired" without listing which fields
  - unifi_create_port_forward: Generic "InvalidPayload" for invalid port numbers
  - unifi_block_client: **CRITICAL** - No validation; accepted malformed MAC address "not-a-mac"
  
  **Critical Findings**:
  1. **MAC validation missing**: unifi_block_client accepted "not-a-mac" and created a record with this invalid MAC. This is a serious validation gap that should be fixed with client-side validation before sending to the API.
  
  2. **API error codes are cryptic**: Most UniFi API errors return generic codes (InvalidPayload, VlanUsed, FirewallRuleFieldsRequired) without explaining which field is wrong or what values are acceptable. This is an API limitation, not a tool generation issue, but it significantly hurts discoverability.
  
  3. **Client-side validation works well**: Where Pydantic validation is in place (data type checking), error messages are excellent. The generator should consider adding more client-side validation for common patterns (MAC addresses, port ranges, enum values).
  
  **Recommendations**:
  - Add client-side MAC address format validation to mutation commands
  - Add client-side port range validation (0-65535)
  - Consider client-side enum validation based on docstrings (purpose values, etc.)
  - Document in tool docstrings that API errors tend to be generic and suggest checking required fields
  
  **Test Verdict**: 6/10 tests failed as expected, 1/10 succeeded when it should have failed (MAC validation), 3/10 had clear errors.

## Tool Coverage

- **Total tools**: 286
- **Tools invoked**: 9
- **Coverage**: 3.1%
- **Not covered** (277):
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
  - `unifi_create_heatmap`
  - `unifi_create_heatmap_point`
  - `unifi_create_hotspot2_config`
  - `unifi_create_hotspot_operator`
  - `unifi_create_hotspot_package`
  - `unifi_create_map`
  - `unifi_create_media_file`
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
  - `unifi_delete_dhcp_option`
  - ... and 227 more

## Actionable Findings

- **Required fields**: Generator should mark required fields more clearly
