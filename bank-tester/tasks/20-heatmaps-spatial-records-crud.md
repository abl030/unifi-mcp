## Task 20: Heatmaps, Spatial Records CRUD

**task_id**: 20-heatmaps-spatial-records-crud

**Objective**: Exercise all tools in the management subsystem.

**Tools to exercise** (15):
- `unifi_create_heatmap`
- `unifi_list_heatmaps`
- `unifi_get_heatmap`
- `unifi_update_heatmap`
- `unifi_delete_heatmap`
- `unifi_create_heatmap_point`
- `unifi_list_heatmap_points`
- `unifi_get_heatmap_point`
- `unifi_update_heatmap_point`
- `unifi_delete_heatmap_point`
- `unifi_create_spatial_record`
- `unifi_list_spatial_records`
- `unifi_get_spatial_record`
- `unifi_update_spatial_record`
- `unifi_delete_spatial_record`

**Steps**:
1. **Create** using `unifi_create_heatmap` with `confirm=True`:
    - `name`: `bt_sys20_heatmap`
2. **List** using `unifi_list_heatmaps` — verify the created resource appears
3. **Get** using `unifi_get_heatmap` with the ID from the create response
4. **Update** using `unifi_update_heatmap` with `confirm=True` — set `name` to `bt_sys20_heatmap_upd`
5. **Get** again using `unifi_get_heatmap` — verify `name` was updated
6. **Create** using `unifi_create_heatmap_point` with `confirm=True`:
    - `name`: `bt_sys20_heatmappoint`
7. **List** using `unifi_list_heatmap_points` — verify the created resource appears
8. **Get** using `unifi_get_heatmap_point` with the ID from the create response
9. **Update** using `unifi_update_heatmap_point` with `confirm=True` — set `name` to `bt_sys20_heatmappoint_upd`
10. **Get** again using `unifi_get_heatmap_point` — verify `name` was updated
11. **Create** using `unifi_create_spatial_record` with `confirm=True`:
    - `name`: `bt_sys20_spatial`
12. **List** using `unifi_list_spatial_records` — verify the created resource appears
13. **Get** using `unifi_get_spatial_record` with the ID from the create response
14. **Update** using `unifi_update_spatial_record` with `confirm=True` — set `name` to `bt_sys20_spatial_upd`
15. **Get** again using `unifi_get_spatial_record` — verify `name` was updated

**Cleanup** (reverse order):
- Delete using `unifi_delete_spatial_record` with `confirm=True` (ID from create step)
- Delete using `unifi_delete_heatmap_point` with `confirm=True` (ID from create step)
- Delete using `unifi_delete_heatmap` with `confirm=True` (ID from create step)

**Expected outcome**: All 15 tools exercised successfully.
