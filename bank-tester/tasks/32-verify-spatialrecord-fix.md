## Task 32: Verify Spatial Record Fix

**task_id**: 32-verify-spatialrecord-fix

**Objective**: Verify that the spatialrecord create fix works (needs `devices: []` array).

**Tools to exercise** (5):
- `unifi_create_spatial_record`
- `unifi_list_spatial_records`
- `unifi_get_spatial_record`
- `unifi_update_spatial_record`
- `unifi_delete_spatial_record`

**Steps**:

1. **Create spatial record** using `unifi_create_spatial_record` with `data={"name": "bt_sys32_spatial", "devices": []}`, `confirm=True` — note the returned `_id`

2. **List spatial records** using `unifi_list_spatial_records` — verify the record appears

3. **Get spatial record** using `unifi_get_spatial_record` with `id=<id from step 1>` — verify full object returned

4. **Update spatial record** using `unifi_update_spatial_record` with `id=<id from step 1>`, `data={"name": "bt_sys32_spatial_upd", "devices": []}`, `confirm=True` — verify name changed

5. **Delete spatial record** using `unifi_delete_spatial_record` with `id=<id from step 1>`, `confirm=True`

**Cleanup** (reverse order):
- Delete handled in step 5

**Expected outcome**: Full CRUD lifecycle works. 0 first-attempt failures.
