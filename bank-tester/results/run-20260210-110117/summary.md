# Bank Tester Results Summary

**Results directory**: `bank-tester/results/run-20260210-110117`

**Tasks analyzed**: 1

## Overall Status

- **success**: 1

**Total tool calls**: 11
**First-attempt failures**: 8
**First-attempt success rate**: 27.3%

## Failure Categories

| Category | Count |
|----------|-------|
| `error_quality_missing` | 6 |
| `error_quality_clear` | 2 |
| `unexpected_error` | 1 |

## Tools With Most Failures

| Tool | Failures |
|------|----------|
| `mcp__unifi__unifi_create_network` | 2 |
| `mcp__unifi__unifi_update_network` | 1 |
| `mcp__unifi__unifi_delete_network` | 1 |
| `mcp__unifi__unifi_get_setting` | 1 |
| `mcp__unifi__unifi_update_setting` | 1 |
| `mcp__unifi__unifi_block_client` | 1 |
| `mcp__unifi__unifi_create_firewall_rule` | 1 |
| `mcp__unifi__unifi_create_port_forward` | 1 |

## Per-Task Results

### 30-adversarial

- **Status**: success
- **Tool calls**: 11
- **First-attempt failures**: 8
- **Cleanup complete**: true
- **Failure details**:
  - `mcp__unifi__unifi_create_network` [error_quality_missing]: Missing required 'name' field, but error message only shows HTTP 400 with MDN link - not helpful
  - `mcp__unifi__unifi_create_network` [error_quality_missing]: Invalid enum value for 'purpose', but error only shows generic HTTP 400 - no mention of valid values
  - `mcp__unifi__unifi_update_network` [error_quality_missing]: Non-existent resource ID, but error only shows HTTP 400 - should be 404 or say "resource not found"
  - `mcp__unifi__unifi_delete_network` [error_quality_missing]: Non-existent resource ID, but error only shows HTTP 400 - should be 404 or say "resource not found"
  - `mcp__unifi__unifi_get_setting` [error_quality_clear]: Clear message - explains exactly what's wrong
  - `mcp__unifi__unifi_update_setting` [error_quality_clear]: Excellent Pydantic error - shows exact problem, expected type, and received type with link to docs
  - `mcp__unifi__unifi_block_client` [unexpected_error]: API silently accepted invalid MAC "not-a-mac" and created a blocked client record - no validation
  - `mcp__unifi__unifi_create_firewall_rule` [error_quality_missing]: Missing required fields, but error only shows HTTP 400 - no hint about which fields are required
  - `mcp__unifi__unifi_create_port_forward` [error_quality_missing]: Invalid port numbers (99999, -1), but error only shows HTTP 400 - no mention of valid port range
- **Notes**: **Error Message Quality Summary:**
  
  CLEAR (2/10):
  - unifi_get_setting: "Setting 'nonexistent_setting_key_xyz' not found" - perfect
  - unifi_update_setting: Pydantic validation with full details - excellent
  
  MISSING (6/10):
  - All network CRUD operations returned generic "Client error '400'" with MDN link
  - No details from UniFi API about what's wrong (missing field, invalid enum, non-existent ID)
  - Port forward and firewall rule creation also generic 400s
  
  UNEXPECTED (1/10):
  - unifi_block_client accepted "not-a-mac" as valid MAC address - no validation
  
  SUCCESS (1/10):
  - unifi_status worked correctly as expected
  
  **Key Findings:**
  1. Pydantic type validation (client-side) works excellently
  2. Setting operations have good error messages
  3. REST CRUD operations return opaque HTTP 400 errors - the UniFi API doesn't provide detailed error messages, and the MCP server doesn't parse or enhance them
  4. MAC address validation is completely missing - API accepts garbage
  5. Most errors give no actionable guidance on how to fix the problem
  
  **Recommendation:** The MCP server should:
  - Add client-side validation for MACs, port ranges, IP formats before sending to API
  - Parse UniFi API error responses (if they contain JSON with details) and extract useful messages
  - Add hints in error messages about common mistakes (e.g., "400 error on create_network - check that 'name' field is present and 'purpose' is one of: corporate, guest, vlan-only, wan")

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
  - ... and 226 more

## Actionable Findings

