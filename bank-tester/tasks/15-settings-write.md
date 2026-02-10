## Task 15: Settings Write

**task_id**: 15-settings-write

**Objective**: Exercise all tools in the settings subsystem.

**Tools to exercise** (2):
- `unifi_get_setting`
- `unifi_update_setting`

**Steps**:
1. **Read setting** using `unifi_get_setting` with `key="snmp"` — note current value of `community`
2. **Update setting** using `unifi_update_setting` with `key="snmp"`, `data={"community": "bt_test_community"}`, `confirm=True`
3. **Verify** using `unifi_get_setting` with `key="snmp"` — confirm `community` changed
4. **Restore** using `unifi_update_setting` with `key="snmp"`, `data={"community": "public"}`, `confirm=True`
5. **Read setting** using `unifi_get_setting` with `key="locale"` — note current value of `timezone` (Read current timezone first, restore after)
6. **Update setting** using `unifi_update_setting` with `key="locale"`, `data={"timezone": "America/New_York"}`, `confirm=True`
7. **Verify** using `unifi_get_setting` with `key="locale"` — confirm `timezone` changed

**Important notes**:
Test unifi_update_setting on safe settings. Read current → update → verify → restore.

**Cleanup** (reverse order):
- No cleanup needed (read-only / settings restored)

**Expected outcome**: All 2 tools exercised successfully.
