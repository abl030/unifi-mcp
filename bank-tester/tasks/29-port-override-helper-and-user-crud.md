## Task 29: Port Override Helper and User CRUD

**task_id**: 29-port-override-helper-and-user-crud

**Objective**: Exercise all tools in the special subsystem.

**Tools to exercise** (5):
- `unifi_set_port_override`
- `unifi_create_user`
- `unifi_list_users`
- `unifi_get_user`
- `unifi_update_user`

**Steps**:
1. **Execute** `unifi_set_port_override` with `confirm=True` **[Hardware-dependent — expect error]** (Requires a device _id and port_overrides array. Expect error without devices)
2. **Create** using `unifi_create_user` with `confirm=True` (Full user CRUD test):
    - `mac`: `00:11:22:33:44:77`
    - `name`: `bt_sys29_user`
3. **List** using `unifi_list_users` — verify the created resource appears
4. **Get** using `unifi_get_user` with the ID from the create response
5. **Update** using `unifi_update_user` with `confirm=True` — set `name` to `bt_sys29_user_upd`
6. **Get** again using `unifi_get_user` — verify `name` was updated

**Cleanup** (reverse order):
- No cleanup needed (read-only / settings restored)

**Expected outcome**: All 5 tools exercised successfully.
