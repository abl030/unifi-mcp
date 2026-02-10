## Task 08: Safe Commands

**task_id**: 08-safe-commands

**Objective**: Exercise all tools in the commands subsystem.

**Tools to exercise** (7):
- `unifi_get_speedtest_status`
- `unifi_check_firmware_update`
- `unifi_get_admins`
- `unifi_list_backups`
- `unifi_archive_all_alarms`
- `unifi_clear_dpi`
- `unifi_restart_http_portal`

**Steps**:
1. **Execute** `unifi_get_speedtest_status` (No params needed)
2. **Execute** `unifi_check_firmware_update` (No params needed)
3. **Execute** `unifi_get_admins` (No params needed)
4. **Execute** `unifi_list_backups` (No params needed)
5. **Execute** `unifi_archive_all_alarms` with `confirm=True` (Safe — just archives all alarms. Requires confirm=True)
6. **Execute** `unifi_clear_dpi` with `confirm=True` (Clears DPI data. Requires confirm=True)
7. **Execute** `unifi_restart_http_portal` with `confirm=True` (Restarts HTTP portal. Requires confirm=True)

**Cleanup** (reverse order):
- No cleanup needed (read-only / settings restored)

**Expected outcome**: All 7 tools exercised successfully.
