## Task 04: Port Profiles and Port Forwards CRUD

**task_id**: 04-port-profiles-and-port-forwards-crud

**Objective**: Exercise all tools in the networking subsystem.

**Tools to exercise** (10):
- `unifi_create_port_profile`
- `unifi_list_port_profiles`
- `unifi_get_port_profile`
- `unifi_update_port_profile`
- `unifi_delete_port_profile`
- `unifi_create_port_forward`
- `unifi_list_port_forwards`
- `unifi_get_port_forward`
- `unifi_update_port_forward`
- `unifi_delete_port_forward`

**Steps**:
1. **Create** using `unifi_create_port_profile` with `confirm=True`:
    - `name`: `bt_sys04_portprofile`
    - `forward`: `customize`
2. **List** using `unifi_list_port_profiles` — verify the created resource appears
3. **Get** using `unifi_get_port_profile` with the ID from the create response
4. **Update** using `unifi_update_port_profile` with `confirm=True` — set `name` to `bt_sys04_portprofile_upd`
5. **Get** again using `unifi_get_port_profile` — verify `name` was updated
6. **Create** using `unifi_create_port_forward` with `confirm=True`:
    - `name`: `bt_sys04_portfwd`
    - `fwd`: `192.168.1.100`
    - `fwd_port`: `8080`
    - `dst_port`: `9090`
    - `proto`: `tcp_udp`
7. **List** using `unifi_list_port_forwards` — verify the created resource appears
8. **Get** using `unifi_get_port_forward` with the ID from the create response
9. **Update** using `unifi_update_port_forward` with `confirm=True` — set `name` to `bt_sys04_portfwd_upd`
10. **Get** again using `unifi_get_port_forward` — verify `name` was updated

**Cleanup** (reverse order):
- Delete using `unifi_delete_port_forward` with `confirm=True` (ID from create step)
- Delete using `unifi_delete_port_profile` with `confirm=True` (ID from create step)

**Expected outcome**: All 10 tools exercised successfully.
