## Task 01: Global Endpoints

**task_id**: 01-global-endpoints

**Objective**: Exercise all tools in the global subsystem.

**Tools to exercise** (5):
- `unifi_status`
- `unifi_self`
- `unifi_sites`
- `unifi_stat_sites`
- `unifi_stat_admin`

**Steps**:
1. **Read** using `unifi_status` (No auth required, returns controller status)
2. **Read** using `unifi_self` (Returns current admin user info)
3. **Read** using `unifi_sites` (Returns list of sites)
4. **Read** using `unifi_stat_sites` (Returns site stats)
5. **Read** using `unifi_stat_admin` (Returns admin stats)

**Cleanup** (reverse order):
- No cleanup needed (read-only / settings restored)

**Expected outcome**: All 5 tools exercised successfully.
