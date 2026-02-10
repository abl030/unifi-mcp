## Task 18: DPI Apps and Groups CRUD

**task_id**: 18-dpi-apps-and-groups-crud

**Objective**: Exercise all tools in the dpi subsystem.

**Tools to exercise** (10):
- `unifi_create_dpi_group`
- `unifi_list_dpi_groups`
- `unifi_get_dpi_group`
- `unifi_update_dpi_group`
- `unifi_delete_dpi_group`
- `unifi_create_dpi_app`
- `unifi_list_dpi_apps`
- `unifi_get_dpi_app`
- `unifi_update_dpi_app`
- `unifi_delete_dpi_app`

**Steps**:
1. **Create** using `unifi_create_dpi_group` with `confirm=True`:
    - `name`: `bt_sys18_dpigroup`
2. **List** using `unifi_list_dpi_groups` — verify the created resource appears
3. **Get** using `unifi_get_dpi_group` with the ID from the create response
4. **Update** using `unifi_update_dpi_group` with `confirm=True` — set `name` to `bt_sys18_dpigroup_upd`
5. **Get** again using `unifi_get_dpi_group` — verify `name` was updated
6. **Create** using `unifi_create_dpi_app` with `confirm=True`:
    - `name`: `bt_sys18_dpiapp`
7. **List** using `unifi_list_dpi_apps` — verify the created resource appears
8. **Get** using `unifi_get_dpi_app` with the ID from the create response
9. **Update** using `unifi_update_dpi_app` with `confirm=True` — set `name` to `bt_sys18_dpiapp_upd`
10. **Get** again using `unifi_get_dpi_app` — verify `name` was updated

**Cleanup** (reverse order):
- Delete using `unifi_delete_dpi_app` with `confirm=True` (ID from create step)
- Delete using `unifi_delete_dpi_group` with `confirm=True` (ID from create step)

**Expected outcome**: All 10 tools exercised successfully.
