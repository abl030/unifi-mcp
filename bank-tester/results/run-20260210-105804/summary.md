# Bank Tester Results Summary

**Results directory**: `bank-tester/results/run-20260210-105804`

**Tasks analyzed**: 1

## Overall Status

- **success**: 1

**Total tool calls**: 37
**First-attempt failures**: 0
**First-attempt success rate**: 100.0%

## Per-Task Results

### 14-settings-read

- **Status**: success
- **Tool calls**: 37
- **First-attempt failures**: 0
- **Cleanup complete**: true
- **Notes**: All 2 tools exercised successfully. Tested unifi_list_settings which returned 29 setting categories,
  then tested unifi_get_setting for all 36 specified keys. 
  
  Of the 36 keys tested:
  - 18 returned data successfully (super_identity, mgmt, guest_access, ntp, connectivity, doh, dpi, 
    element_adopt, ether_lighting, global_switch, ips, lcm, magic_site_to_site_vpn, radio_ai, 
    rsyslogd, super_cloudaccess, super_mgmt, teleport, usg)
  - 18 returned "Setting not found" (snmp, country, locale, auto_speedtest, baresip, broadcast, 
    global_ap, network_optimization, porta, radius, super_events, super_fwupdate, super_mail, 
    super_sdn, super_smtp, usw)
  
  The "not found" results are expected behavior - these settings don't exist until explicitly 
  configured or are not applicable to this controller version. The tool correctly returns null 
  with a clear message for missing settings rather than erroring.
  
  Tool discoverability: Excellent. Both tools have clear names and the get_setting docstring 
  clearly shows it requires a key parameter with examples (super_identity, snmp).
  
  No issues encountered - the settings API pattern is straightforward and well-documented.

## Tool Coverage

- **Total tools**: 286
- **Tools invoked**: 2
- **Coverage**: 0.7%
- **Not covered** (284):
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
  - ... and 234 more
