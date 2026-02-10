## Task 17: V2 Traffic Rules, Routes, Clients, AP Groups

**task_id**: 17-v2-traffic-rules-routes-clients-ap-groups

**Objective**: Exercise all tools in the v2 subsystem.

**Tools to exercise** (9):
- `unifi_list_traffic_rules`
- `unifi_create_traffic_rule`
- `unifi_update_traffic_rule`
- `unifi_delete_traffic_rule`
- `unifi_list_traffic_routes`
- `unifi_update_traffic_route`
- `unifi_list_active_clients`
- `unifi_list_clients_history`
- `unifi_list_ap_groups`

**Steps**:
1. **List** using `unifi_list_traffic_rules`
2. **Create** using `unifi_create_traffic_rule` with `confirm=True`:
    - `description`: `bt_sys17_traffic_rule`
    - `enabled`: `True`
    - `action`: `BLOCK`
    - `matching_target`: `INTERNET`
    - `target_devices`: `[{'type': 'ALL'}]`
3. **Update** using `unifi_update_traffic_rule` with `confirm=True` — set `description` to `bt_sys17_traffic_rule_upd`
4. **List** using `unifi_list_traffic_routes`
5. **Update** using `unifi_update_traffic_route` with `confirm=True` — read current data, modify, and PUT back
6. **List** using `unifi_list_active_clients`
7. **List** using `unifi_list_clients_history`
8. **List** using `unifi_list_ap_groups`

**Cleanup** (reverse order):
- Delete using `unifi_delete_traffic_rule` with `confirm=True` (ID from create step)

**Expected outcome**: All 9 tools exercised successfully.
