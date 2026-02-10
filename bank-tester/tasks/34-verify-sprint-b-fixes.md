## Task 34: Verify Sprint B Fixes

**task_id**: 34-verify-sprint-b-fixes

**Objective**: Verify all Sprint B changes: Docker startup race fix (global endpoints work), reclassified tools that should now succeed, spatial record CRUD, and confirm `delete_user` tool no longer exists.

**Tools to exercise** (16 unique tools, ~20 calls):

### Section A: Global Endpoints (startup race fix — previously failed with JSON parse error)

1. **Call** `unifi_self` — should return admin profile data
2. **Call** `unifi_list_sites` — should return site list
3. **Call** `unifi_list_stat_sites` — should return site stats
4. **Call** `unifi_list_stat_admin` — should return admin stats

### Section B: Client Commands (reclassified from hardware-dependent to WORKS)

5. **Create a user** first: `unifi_create_user` with `data={"mac": "00:34:56:78:9A:BC", "name": "bt_sys34_user"}`, `confirm=True`
   - Previously failed with MacAlreadyRegistered (stale MAC)
6. **Block client**: `unifi_block_client` with `mac="00:34:56:78:9A:BC"`, `confirm=True`
   - Previously classified as hardware-dependent, now confirmed WORKS
7. **Unblock client**: `unifi_unblock_client` with `mac="00:34:56:78:9A:BC"`, `confirm=True`
   - Previously classified as hardware-dependent, now confirmed WORKS
8. **Authorize guest**: `unifi_authorize_guest` with `mac="00:34:56:78:9A:BC"`, `minutes=60`, `confirm=True`
   - Previously classified as hardware-dependent, now confirmed WORKS
9. **Unauthorize guest**: `unifi_unauthorize_guest` with `mac="00:34:56:78:9A:BC"`, `confirm=True`
   - Previously classified as hardware-dependent, now confirmed WORKS

### Section C: Spatial Record CRUD (verified by Opus, confirming with Sonnet)

10. **Create map** (dependency): `unifi_create_map` with `data={"name": "bt_sys34_map"}`, `confirm=True` — note the `_id`
11. **Create spatial record**: `unifi_create_spatial_record` with `data={"name": "bt_sys34_spatial", "devices": [], "description": "Sprint B test"}`, `confirm=True`
    - Previously failed with api.err.Invalid (missing fields)
12. **List spatial records**: `unifi_list_spatial_records` — verify created record appears
13. **Delete spatial record**: `unifi_delete_spatial_record` with the `_id` from step 11, `confirm=True`

### Section D: delete_user Tool Removed

14. **Attempt** `unifi_delete_user` — this tool should NOT EXIST. If you cannot find it in your available tools, that's the expected behavior. Record this as a SUCCESS.
    - Previously this tool existed but always returned api.err.NotFound
    - The correct way to remove users is `unifi_forget_client`

15. **Forget client**: `unifi_forget_client` with `macs=["00:34:56:78:9A:BC"]`, `confirm=True`
    - This is the correct replacement for delete_user

### Section E: Grant Super Admin (reclassified from API limitation to WORKS)

16. **List admins**: `unifi_get_admins` — get the admin `_id`
17. **Grant super admin**: `unifi_grant_super_admin` with `admin=<admin_id>`, `confirm=True`
    - Previously classified as API limitation, now confirmed WORKS

### Cleanup

18. Delete the map from step 10: `unifi_delete_map` with `_id`, `confirm=True`
