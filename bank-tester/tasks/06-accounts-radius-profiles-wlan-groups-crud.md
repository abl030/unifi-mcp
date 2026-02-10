## Task 06: Accounts, RADIUS Profiles, WLAN Groups CRUD

**task_id**: 06-accounts-radius-profiles-wlan-groups-crud

**Objective**: Exercise all tools in the networking subsystem.

**Tools to exercise** (15):
- `unifi_create_account`
- `unifi_list_accounts`
- `unifi_get_account`
- `unifi_update_account`
- `unifi_delete_account`
- `unifi_create_radius_profile`
- `unifi_list_radius_profiles`
- `unifi_get_radius_profile`
- `unifi_update_radius_profile`
- `unifi_delete_radius_profile`
- `unifi_create_wlan_group`
- `unifi_list_wlan_groups`
- `unifi_get_wlan_group`
- `unifi_update_wlan_group`
- `unifi_delete_wlan_group`

**Steps**:
1. **Create** using `unifi_create_account` with `confirm=True`:
    - `name`: `bt_sys06_account`
    - `x_password`: `testpassword`
2. **List** using `unifi_list_accounts` — verify the created resource appears
3. **Get** using `unifi_get_account` with the ID from the create response
4. **Update** using `unifi_update_account` with `confirm=True` — set `name` to `bt_sys06_account_upd`
5. **Get** again using `unifi_get_account` — verify `name` was updated
6. **Create** using `unifi_create_radius_profile` with `confirm=True`:
    - `name`: `bt_sys06_radius`
    - `auth_servers`: `[{'ip': '192.168.1.200', 'port': 1812, 'x_secret': 'secret'}]`
7. **List** using `unifi_list_radius_profiles` — verify the created resource appears
8. **Get** using `unifi_get_radius_profile` with the ID from the create response
9. **Update** using `unifi_update_radius_profile` with `confirm=True` — set `name` to `bt_sys06_radius_upd`
10. **Get** again using `unifi_get_radius_profile` — verify `name` was updated
11. **Create** using `unifi_create_wlan_group` with `confirm=True`:
    - `name`: `bt_sys06_wlangroup`
12. **List** using `unifi_list_wlan_groups` — verify the created resource appears
13. **Get** using `unifi_get_wlan_group` with the ID from the create response
14. **Update** using `unifi_update_wlan_group` with `confirm=True` — set `name` to `bt_sys06_wlangroup_upd`
15. **Get** again using `unifi_get_wlan_group` — verify `name` was updated

**Cleanup** (reverse order):
- Delete using `unifi_delete_wlan_group` with `confirm=True` (ID from create step)
- Delete using `unifi_delete_radius_profile` with `confirm=True` (ID from create step)
- Delete using `unifi_delete_account` with `confirm=True` (ID from create step)

**Expected outcome**: All 15 tools exercised successfully.
