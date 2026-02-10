## Task 25: Hotspot and Voucher Commands

**task_id**: 25-hotspot-and-voucher-commands

**Objective**: Exercise all tools in the commands subsystem.

**Tools to exercise** (5):
- `unifi_create_voucher`
- `unifi_hotspot_authorize_guest`
- `unifi_extend_guest_validity`
- `unifi_revoke_voucher`
- `unifi_delete_voucher`

**Steps**:
1. **Execute** `unifi_create_voucher` with `confirm=True` (Create a voucher. Requires confirm=True):
    - `expire`: `1440`
    - `n`: `1`
    - `quota`: `1`
2. **Execute** `unifi_hotspot_authorize_guest` with `confirm=True` (Authorize hotspot guest. Requires confirm=True):
    - `mac`: `00:11:22:33:44:66`
    - `minutes`: `60`
3. **Execute** `unifi_extend_guest_validity` with `confirm=True` (Extend guest validity. Requires confirm=True. Use _id from create_voucher):
    - `_id`: `<voucher_id>`
4. **Execute** `unifi_revoke_voucher` with `confirm=True` (Revoke voucher. Requires confirm=True):
    - `_id`: `<voucher_id>`
5. **Execute** `unifi_delete_voucher` with `confirm=True` (Delete voucher. Requires confirm=True. Run LAST):
    - `_id`: `<voucher_id>`

**Cleanup** (reverse order):
- No cleanup needed (read-only / settings restored)

**Expected outcome**: All 5 tools exercised successfully.
