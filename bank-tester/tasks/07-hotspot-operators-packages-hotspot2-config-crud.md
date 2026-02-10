## Task 07: Hotspot Operators, Packages, Hotspot2 Config CRUD

**task_id**: 07-hotspot-operators-packages-hotspot2-config-crud

**Objective**: Exercise all tools in the hotspot subsystem.

**Tools to exercise** (15):
- `unifi_create_hotspot_operator`
- `unifi_list_hotspot_operators`
- `unifi_get_hotspot_operator`
- `unifi_update_hotspot_operator`
- `unifi_delete_hotspot_operator`
- `unifi_create_hotspot_package`
- `unifi_list_hotspot_packages`
- `unifi_get_hotspot_package`
- `unifi_update_hotspot_package`
- `unifi_delete_hotspot_package`
- `unifi_create_hotspot2_config`
- `unifi_list_hotspot2_configs`
- `unifi_get_hotspot2_config`
- `unifi_update_hotspot2_config`
- `unifi_delete_hotspot2_config`

**Steps**:
1. **Create** using `unifi_create_hotspot_operator` with `confirm=True`:
    - `name`: `bt_sys07_operator`
    - `x_password`: `testpass123`
2. **List** using `unifi_list_hotspot_operators` — verify the created resource appears
3. **Get** using `unifi_get_hotspot_operator` with the ID from the create response
4. **Update** using `unifi_update_hotspot_operator` with `confirm=True` — set `name` to `bt_sys07_operator_upd`
5. **Get** again using `unifi_get_hotspot_operator` — verify `name` was updated
6. **Create** using `unifi_create_hotspot_package` with `confirm=True`:
    - `name`: `bt_sys07_package`
    - `amount`: `0`
    - `currency`: `USD`
7. **List** using `unifi_list_hotspot_packages` — verify the created resource appears
8. **Get** using `unifi_get_hotspot_package` with the ID from the create response
9. **Update** using `unifi_update_hotspot_package` with `confirm=True` — set `name` to `bt_sys07_package_upd`
10. **Get** again using `unifi_get_hotspot_package` — verify `name` was updated
11. **Create** using `unifi_create_hotspot2_config` with `confirm=True`:
    - `name`: `bt_sys07_hs2conf`
12. **List** using `unifi_list_hotspot2_configs` — verify the created resource appears
13. **Get** using `unifi_get_hotspot2_config` with the ID from the create response
14. **Update** using `unifi_update_hotspot2_config` with `confirm=True` — set `name` to `bt_sys07_hs2conf_upd`
15. **Get** again using `unifi_get_hotspot2_config` — verify `name` was updated

**Cleanup** (reverse order):
- Delete using `unifi_delete_hotspot2_config` with `confirm=True` (ID from create step)
- Delete using `unifi_delete_hotspot_package` with `confirm=True` (ID from create step)
- Delete using `unifi_delete_hotspot_operator` with `confirm=True` (ID from create step)

**Expected outcome**: All 15 tools exercised successfully.
