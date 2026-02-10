## Task 23: Client Commands

**task_id**: 23-client-commands

**Objective**: Exercise all tools in the commands subsystem.

**Tools to exercise** (10):
- `unifi_create_user`
- `unifi_list_users`
- `unifi_get_user`
- `unifi_block_client`
- `unifi_unblock_client`
- `unifi_kick_client`
- `unifi_reconnect_client`
- `unifi_authorize_guest`
- `unifi_unauthorize_guest`
- `unifi_forget_client`

**Steps**:
1. **Create** using `unifi_create_user` with `confirm=True` (Create a known client record to test commands against):
    - `mac`: `00:11:22:33:44:55`
    - `name`: `bt_sys23_client`
2. **List** using `unifi_list_users` — verify the created resource appears
3. **Get** using `unifi_get_user` with the ID from the create response
4. **Execute** `unifi_block_client` with `confirm=True` (Block client by MAC. Requires confirm=True):
    - `mac`: `00:11:22:33:44:55`
5. **Execute** `unifi_unblock_client` with `confirm=True` (Unblock client. Requires confirm=True):
    - `mac`: `00:11:22:33:44:55`
6. **Execute** `unifi_kick_client` with `confirm=True` (Kick client. Requires confirm=True. May return error if client not connected):
    - `mac`: `00:11:22:33:44:55`
7. **Execute** `unifi_reconnect_client` with `confirm=True` (Reconnect client. Requires confirm=True. May return error if client not connected):
    - `mac`: `00:11:22:33:44:55`
8. **Execute** `unifi_authorize_guest` with `confirm=True` (Authorize guest for 60 min. Requires confirm=True):
    - `mac`: `00:11:22:33:44:55`
    - `minutes`: `60`
9. **Execute** `unifi_unauthorize_guest` with `confirm=True` (Unauthorize guest. Requires confirm=True):
    - `mac`: `00:11:22:33:44:55`
10. **Execute** `unifi_forget_client` with `confirm=True` (Forget client. Requires confirm=True. Uses 'macs' list param. Run LAST (deletes the user).):
    - `macs`: `['00:11:22:33:44:55']`

**Cleanup** (reverse order):
- No cleanup needed (read-only / settings restored)

**Expected outcome**: All 10 tools exercised successfully.
