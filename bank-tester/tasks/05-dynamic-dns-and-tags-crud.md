## Task 05: Dynamic DNS and Tags CRUD

**task_id**: 05-dynamic-dns-and-tags-crud

**Objective**: Exercise all tools in the networking subsystem.

**Tools to exercise** (10):
- `unifi_create_dynamic_dns`
- `unifi_list_dynamic_dns_entries`
- `unifi_get_dynamic_dns`
- `unifi_update_dynamic_dns`
- `unifi_delete_dynamic_dns`
- `unifi_create_tag`
- `unifi_list_tags`
- `unifi_get_tag`
- `unifi_update_tag`
- `unifi_delete_tag`

**Steps**:
1. **Create** using `unifi_create_dynamic_dns` with `confirm=True`:
    - `service`: `dyndns`
    - `host_name`: `bt_sys05.example.com`
    - `login`: `testuser`
    - `x_password`: `testpass`
2. **List** using `unifi_list_dynamic_dns_entries` — verify the created resource appears
3. **Get** using `unifi_get_dynamic_dns` with the ID from the create response
4. **Update** using `unifi_update_dynamic_dns` with `confirm=True` — set `host_name` to `bt_sys05_upd.example.com`
5. **Get** again using `unifi_get_dynamic_dns` — verify `host_name` was updated
6. **Create** using `unifi_create_tag` with `confirm=True`:
    - `name`: `bt_sys05_tag`
    - `member_table`: `[]`
7. **List** using `unifi_list_tags` — verify the created resource appears
8. **Get** using `unifi_get_tag` with the ID from the create response
9. **Update** using `unifi_update_tag` with `confirm=True` — set `name` to `bt_sys05_tag_upd`
10. **Get** again using `unifi_get_tag` — verify `name` was updated

**Cleanup** (reverse order):
- Delete using `unifi_delete_tag` with `confirm=True` (ID from create step)
- Delete using `unifi_delete_dynamic_dns` with `confirm=True` (ID from create step)

**Expected outcome**: All 10 tools exercised successfully.
