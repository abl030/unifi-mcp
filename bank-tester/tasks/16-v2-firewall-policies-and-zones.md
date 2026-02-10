## Task 16: V2 Firewall Policies and Zones

**task_id**: 16-v2-firewall-policies-and-zones

**Objective**: Exercise all tools in the v2 subsystem.

**Tools to exercise** (6):
- `unifi_list_firewall_policies`
- `unifi_create_firewall_policy`
- `unifi_update_firewall_policy`
- `unifi_delete_firewall_policy`
- `unifi_list_firewall_zones`
- `unifi_update_firewall_zone`

**Steps**:
1. **List** using `unifi_list_firewall_policies`
2. **Create** using `unifi_create_firewall_policy` with `confirm=True`:
    - `name`: `bt_sys16_fw_policy`
    - `enabled`: `True`
3. **Update** using `unifi_update_firewall_policy` with `confirm=True` — set `name` to `bt_sys16_fw_policy_upd`
4. **List** using `unifi_list_firewall_zones`
5. **Update** using `unifi_update_firewall_zone` with `confirm=True` — read current data, modify, and PUT back

**Cleanup** (reverse order):
- Delete using `unifi_delete_firewall_policy` with `confirm=True` (ID from create step)

**Expected outcome**: All 6 tools exercised successfully.
