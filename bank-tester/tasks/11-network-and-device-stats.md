## Task 11: Network and Device Stats

**task_id**: 11-network-and-device-stats

**Objective**: Exercise all tools in the stats subsystem.

**Tools to exercise** (8):
- `unifi_list_routing_stats`
- `unifi_list_port_forward_stats`
- `unifi_list_dynamic_dns_stats`
- `unifi_list_sdn_status`
- `unifi_list_devices`
- `unifi_list_devices_basic`
- `unifi_list_current_channels`
- `unifi_list_spectrum_scans`

**Steps**:
1. **Read stat** using `unifi_list_routing_stats`
2. **Read stat** using `unifi_list_port_forward_stats`
3. **Read stat** using `unifi_list_dynamic_dns_stats`
4. **Read stat** using `unifi_list_sdn_status`
5. **Read stat** using `unifi_list_devices`
6. **Read stat** using `unifi_list_devices_basic`
7. **Read stat** using `unifi_list_current_channels`
8. **Read stat** using `unifi_list_spectrum_scans`

**Cleanup** (reverse order):
- No cleanup needed (read-only / settings restored)

**Expected outcome**: All 8 tools exercised successfully.
