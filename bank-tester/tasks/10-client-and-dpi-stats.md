## Task 10: Client and DPI Stats

**task_id**: 10-client-and-dpi-stats

**Objective**: Exercise all tools in the stats subsystem.

**Tools to exercise** (8):
- `unifi_list_clients`
- `unifi_list_client_dpi`
- `unifi_list_site_dpi`
- `unifi_list_all_users`
- `unifi_list_sessions`
- `unifi_list_guests`
- `unifi_list_authorizations`
- `unifi_list_dpi_stats`

**Steps**:
1. **Read stat** using `unifi_list_clients`
2. **Read stat** using `unifi_list_client_dpi`
3. **Read stat** using `unifi_list_site_dpi`
4. **Read stat** using `unifi_list_all_users`
5. **Read stat** using `unifi_list_sessions` (Requires POST with mac parameter)
6. **Read stat** using `unifi_list_guests`
7. **Read stat** using `unifi_list_authorizations`
8. **Read stat** using `unifi_list_dpi_stats`

**Cleanup** (reverse order):
- No cleanup needed (read-only / settings restored)

**Expected outcome**: All 8 tools exercised successfully.
