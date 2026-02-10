# Bank Tester Results Summary

**Results directory**: `bank-tester/results/run-20260210-140135`

**Tasks analyzed**: 1

## Overall Status

- **success**: 1

**Total tool calls**: 8
**First-attempt failures**: 0
**First-attempt success rate**: 100.0%

## Per-Task Results

### 22-admin-management-commands

- **Status**: success
- **Tool calls**: 8
- **First-attempt failures**: 0
- **Cleanup complete**: true
- **Notes**: All 8 admin management command tools executed successfully on first attempt.
  
  Key observations:
  - unifi_create_admin: Created admin successfully with required fields (name, email, x_password, role)
  - unifi_add_site: Second site created for cross-site admin assignment test
  - unifi_assign_existing_admin: Successfully assigned existing admin to second site
  - unifi_invite_admin: Email invitation sent successfully (mailpit SMTP configured)
  - unifi_update_admin: Role change from admin to readonly worked correctly
  - unifi_grant_super_admin: Super admin privileges granted successfully
  - unifi_revoke_super_admin: Super admin privileges revoked successfully (on different admin, not self)
  - unifi_revoke_admin: Admin fully deleted (cleanup handled by final revoke)
  
  Tool discoverability: All tools had clear names and complete docstrings.
  confirm=True pattern: Worked as expected for all mutations.
  No friction points encountered.

## Tool Coverage

- **Total tools**: 283
- **Tools invoked**: 8
- **Coverage**: 2.8%
- **Not covered** (275):
  - `unifi_adopt_device`
  - `unifi_advanced_adopt_device`
  - `unifi_alarm_archive`
  - `unifi_archive_alarm`
  - `unifi_archive_all_alarms`
  - `unifi_authorize_guest`
  - `unifi_block_client`
  - `unifi_cable_test`
  - `unifi_cancel_migrate_device`
  - `unifi_cancel_rolling_upgrade`
  - `unifi_check_firmware_update`
  - `unifi_clear_dpi`
  - `unifi_create_account`
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
  - `unifi_delete_backup`
  - `unifi_delete_broadcast_group`
  - `unifi_delete_device`
  - `unifi_delete_dhcp_option`
  - ... and 225 more
