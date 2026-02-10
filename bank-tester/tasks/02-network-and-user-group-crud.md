## Task 02: Network and User Group CRUD

**task_id**: 02-network-and-user-group-crud

**Objective**: Exercise all tools in the networking subsystem.

**Tools to exercise** (10):
- `unifi_create_network`
- `unifi_list_networks`
- `unifi_get_network`
- `unifi_update_network`
- `unifi_delete_network`
- `unifi_create_user_group`
- `unifi_list_user_groups`
- `unifi_get_user_group`
- `unifi_update_user_group`
- `unifi_delete_user_group`

**Steps**:
1. **Create** using `unifi_create_network` with `confirm=True`:
    - `name`: `bt_sys02_network`
    - `purpose`: `vlan-only`
    - `vlan_enabled`: `True`
    - `vlan`: `999`
2. **List** using `unifi_list_networks` — verify the created resource appears
3. **Get** using `unifi_get_network` with the ID from the create response
4. **Update** using `unifi_update_network` with `confirm=True` — set `name` to `bt_sys02_updated`
5. **Get** again using `unifi_get_network` — verify `name` was updated
6. **Create** using `unifi_create_user_group` with `confirm=True`:
    - `name`: `bt_sys02_usergroup`
7. **List** using `unifi_list_user_groups` — verify the created resource appears
8. **Get** using `unifi_get_user_group` with the ID from the create response
9. **Update** using `unifi_update_user_group` with `confirm=True` — set `name` to `bt_sys02_usergroup_upd`
10. **Get** again using `unifi_get_user_group` — verify `name` was updated

**Cleanup** (reverse order):
- Delete using `unifi_delete_user_group` with `confirm=True` (ID from create step)
- Delete using `unifi_delete_network` with `confirm=True` (ID from create step)

**Expected outcome**: All 10 tools exercised successfully.
