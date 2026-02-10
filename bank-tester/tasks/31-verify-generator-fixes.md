## Task 31: Verify Generator Fixes

**task_id**: 31-verify-generator-fixes

**Objective**: Verify that all 21 generator-fixable first-attempt failures from the Sonnet first pass are now resolved. Each step below targets a tool+scenario that previously failed.

**Tools to exercise** (14 unique tools, 21 calls):
- `unifi_update_setting` (6 calls — previously wrong endpoint)
- `unifi_list_sessions` (1 call — previously missing POST body)
- `unifi_create_hotspot_package` (1 call — previously missing field docs)
- `unifi_create_dhcp_option` (1 call — previously missing field docs)
- `unifi_create_heatmap` (1 call — previously missing field docs)
- `unifi_create_heatmap_point` (1 call — previously missing field docs)
- `unifi_create_spatial_record` (1 call — previously missing field docs)
- `unifi_update_schedule_task` (1 call — previously full-object needed)
- `unifi_create_traffic_rule` (1 call — previously missing enum values)
- `unifi_update_traffic_rule` (1 call — previously full-object needed)
- `unifi_clear_dpi` (1 call — previously wrong command name)
- `unifi_block_client` (1 call — previously no MAC validation)
- `unifi_create_map` (1 call — needed for heatmap/spatial)
- `unifi_create_schedule_task` (1 call — needed for schedule update)

**Steps**:

### Section A: Settings Update (6 previously-failing calls)

1. **Read setting** using `unifi_get_setting` with `key="snmp"` — note current values
2. **Update setting** using `unifi_update_setting` with `key="snmp"`, `data={"community": "bt_sys31_snmp"}`, `confirm=True` — PREVIOUSLY FAILED with api.err.Invalid
3. **Verify** using `unifi_get_setting` with `key="snmp"` — confirm community changed
4. **Restore** using `unifi_update_setting` with `key="snmp"`, `data={"community": "public"}`, `confirm=True`

5. **Read setting** using `unifi_get_setting` with `key="ntp"` — note current values
6. **Update setting** using `unifi_update_setting` with `key="ntp"`, `data={"ntp_server_1": "time.google.com"}`, `confirm=True` — PREVIOUSLY FAILED
7. **Verify** using `unifi_get_setting` with `key="ntp"` — confirm ntp_server_1 changed
8. **Restore** using `unifi_update_setting` with `key="ntp"`, `data={"ntp_server_1": ""}`, `confirm=True`

9. **Update setting** using `unifi_update_setting` with `key="locale"`, `data={"timezone": "America/New_York"}`, `confirm=True` — PREVIOUSLY FAILED
10. **Update setting** using `unifi_update_setting` with `key="mgmt"`, `data={"led_enabled": false}`, `confirm=True` — PREVIOUSLY FAILED
11. **Update setting** using `unifi_update_setting` with `key="connectivity"`, `data={"uplink_type": "gateway"}`, `confirm=True` — PREVIOUSLY FAILED
12. **Update setting** using `unifi_update_setting` with `key="guest_access"`, `data={"auth": "none"}`, `confirm=True` — PREVIOUSLY FAILED

### Section B: Sessions Stat (1 previously-failing call)

13. **Read stat** using `unifi_list_sessions` — PREVIOUSLY FAILED with api.err.InvalidArgs. Should now work with built-in POST body.

### Section C: Undocumented Resource Creates (5 previously-failing calls)

14. **Create map first** using `unifi_create_map` with `data={"name": "bt_sys31_map"}`, `confirm=True` — note the returned `_id`

15. **Create hotspot package** using `unifi_create_hotspot_package` with `data={"name": "bt_sys31_pkg", "amount": 0, "currency": "USD", "duration": 60, "bytes": 0}`, `confirm=True` — PREVIOUSLY FAILED (undocumented fields)

16. **Create DHCP option** using `unifi_create_dhcp_option` with `data={"name": "bt_sys31_dhcp", "code": 252, "value": "http://example.com/wpad.dat"}`, `confirm=True` — PREVIOUSLY FAILED (undocumented fields)

17. **Create heatmap** using `unifi_create_heatmap` with `data={"name": "bt_sys31_heatmap", "map_id": "<map_id from step 14>"}`, `confirm=True` — PREVIOUSLY FAILED (undocumented fields)

18. **Create heatmap point** using `unifi_create_heatmap_point` with `data={"heatmap_id": "<heatmap_id from step 17>", "x": 0.5, "y": 0.5}`, `confirm=True` — PREVIOUSLY FAILED (undocumented fields)

19. **Create spatial record** using `unifi_create_spatial_record` with `data={"name": "bt_sys31_spatial", "devices": []}`, `confirm=True` — PREVIOUSLY FAILED (undocumented fields)

### Section D: Full-Object Update Pattern (2 previously-failing calls)

20. **Create schedule task** using `unifi_create_schedule_task` with `data={"name": "bt_sys31_task", "action": "upgrade", "cron_expr": "0 3 * * 6"}`, `confirm=True` — note the full returned object

21. **Update schedule task (full object)** — First call `unifi_get_schedule_task` with the ID from step 20. Take the FULL returned object, change the `name` field to `"bt_sys31_task_upd"`, then call `unifi_update_schedule_task` with `id=<id>`, `data=<full modified object>`, `confirm=True` — PREVIOUSLY FAILED (partial update rejected)

22. **Create traffic rule** using `unifi_create_traffic_rule` with `data={"action": "BLOCK", "enabled": true, "matching_target": "INTERNET", "target_devices": [{"type": "ALL_CLIENTS"}], "description": "bt_sys31_rule"}`, `confirm=True` — PREVIOUSLY FAILED (missing enum values)

23. **Update traffic rule (full object)** — First call `unifi_list_traffic_rules` to get the rule from step 22. Take the FULL returned object, change `description` to `"bt_sys31_rule_upd"`, then call `unifi_update_traffic_rule` with `id=<id>`, `data=<full modified object>`, `confirm=True` — PREVIOUSLY FAILED (partial update rejected)

### Section E: DPI Reset (1 previously-failing call)

24. **Clear DPI** using `unifi_clear_dpi` with `confirm=True` — PREVIOUSLY FAILED with 404 on cmd/stat (command name was wrong)

### Section F: MAC Validation (1 previously-failing call)

25. **Block client with bad MAC** using `unifi_block_client` with `mac="not-a-mac"`, `confirm=True` — should now return a validation error BEFORE hitting the API. PREVIOUSLY the API accepted the bad MAC silently.

**Important notes**:
- Steps 1-12: Test the new `set/setting/{key}` endpoint path (was `rest/setting/{id}`)
- Step 13: Tool now has built-in POST body `{"type":"all","start":0,"end":9999999999}`
- Steps 15-19: Docstrings now document required fields — use exactly the fields shown
- Steps 21, 23: Must send the FULL object on update, not just changed fields
- Step 24: Command renamed from `clear-dpi` to `reset-dpi`
- Step 25: Client-side MAC validation should catch the bad format

**Cleanup** (reverse order):
- Delete traffic rule from step 22 using `unifi_delete_traffic_rule`
- Delete schedule task from step 20 using `unifi_delete_schedule_task`
- Delete spatial record from step 19 using `unifi_delete_spatial_record`
- Delete heatmap point from step 18 using `unifi_delete_heatmap_point`
- Delete heatmap from step 17 using `unifi_delete_heatmap`
- Delete DHCP option from step 16 using `unifi_delete_dhcp_option`
- Delete hotspot package from step 15 using `unifi_delete_hotspot_package`
- Delete map from step 14 using `unifi_delete_map`
- Settings restored inline (steps 4, 8)

**Expected outcome**: All 21 previously-failing calls now succeed on first attempt. 0 first-attempt failures.
