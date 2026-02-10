## Task 19: Maps, Schedules, DHCP Options CRUD

**task_id**: 19-maps-schedules-dhcp-options-crud

**Objective**: Exercise all tools in the management subsystem.

**Tools to exercise** (15):
- `unifi_create_map`
- `unifi_list_maps`
- `unifi_get_map`
- `unifi_update_map`
- `unifi_delete_map`
- `unifi_create_schedule_task`
- `unifi_list_schedule_tasks`
- `unifi_get_schedule_task`
- `unifi_update_schedule_task`
- `unifi_delete_schedule_task`
- `unifi_create_dhcp_option`
- `unifi_list_dhcp_options`
- `unifi_get_dhcp_option`
- `unifi_update_dhcp_option`
- `unifi_delete_dhcp_option`

**Steps**:
1. **Create** using `unifi_create_map` with `confirm=True`:
    - `name`: `bt_sys19_map`
2. **List** using `unifi_list_maps` — verify the created resource appears
3. **Get** using `unifi_get_map` with the ID from the create response
4. **Update** using `unifi_update_map` with `confirm=True` — set `name` to `bt_sys19_map_upd`
5. **Get** again using `unifi_get_map` — verify `name` was updated
6. **Create** using `unifi_create_schedule_task` with `confirm=True`:
    - `name`: `bt_sys19_schedule`
    - `action`: `upgrade`
    - `cron_expr`: `0 2 * * *`
7. **List** using `unifi_list_schedule_tasks` — verify the created resource appears
8. **Get** using `unifi_get_schedule_task` with the ID from the create response
9. **Update** using `unifi_update_schedule_task` with `confirm=True` — set `name` to `bt_sys19_schedule_upd`
10. **Get** again using `unifi_get_schedule_task` — verify `name` was updated
11. **Create** using `unifi_create_dhcp_option` with `confirm=True`:
    - `name`: `bt_sys19_dhcpoption`
12. **List** using `unifi_list_dhcp_options` — verify the created resource appears
13. **Get** using `unifi_get_dhcp_option` with the ID from the create response
14. **Update** using `unifi_update_dhcp_option` with `confirm=True` — set `name` to `bt_sys19_dhcpoption_upd`
15. **Get** again using `unifi_get_dhcp_option` — verify `name` was updated

**Cleanup** (reverse order):
- Delete using `unifi_delete_dhcp_option` with `confirm=True` (ID from create step)
- Delete using `unifi_delete_schedule_task` with `confirm=True` (ID from create step)
- Delete using `unifi_delete_map` with `confirm=True` (ID from create step)

**Expected outcome**: All 15 tools exercised successfully.
