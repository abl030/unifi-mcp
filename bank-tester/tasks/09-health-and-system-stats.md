## Task 09: Health and System Stats

**task_id**: 09-health-and-system-stats

**Objective**: Exercise all tools in the stats subsystem.

**Tools to exercise** (8):
- `unifi_list_health`
- `unifi_list_sysinfo`
- `unifi_list_dashboard`
- `unifi_list_country_codes`
- `unifi_list_events`
- `unifi_list_alarms`
- `unifi_list_stat_events`
- `unifi_list_stat_alarms`

**Steps**:
1. **Read stat** using `unifi_list_health`
2. **Read stat** using `unifi_list_sysinfo`
3. **Read stat** using `unifi_list_dashboard`
4. **Read stat** using `unifi_list_country_codes`
5. **Read** using `unifi_list_events` (REST read-only endpoint)
6. **Read** using `unifi_list_alarms` (REST read-only endpoint)
7. **Read stat** using `unifi_list_stat_events`
8. **Read stat** using `unifi_list_stat_alarms`

**Cleanup** (reverse order):
- No cleanup needed (read-only / settings restored)

**Expected outcome**: All 8 tools exercised successfully.
