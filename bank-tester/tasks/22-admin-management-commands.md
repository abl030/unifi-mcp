## Task 22: Admin Management Commands

**task_id**: 22-admin-management-commands

**Objective**: Exercise all tools in the commands subsystem.

**Tools to exercise** (8):
- `unifi_create_admin`
- `unifi_assign_existing_admin`
- `unifi_invite_admin`
- `unifi_update_admin`
- `unifi_revoke_admin`
- `unifi_grant_super_admin`
- `unifi_revoke_super_admin`
- `unifi_delete_admin`

**Steps**:
1. **Execute** `unifi_create_admin` with `confirm=True` (Creates a new admin. Requires confirm=True):
    - `name`: `bt_sys22_admin`
    - `email`: `bt_sys22@test.local`
    - `x_password`: `TestPassword123!`
    - `role`: `admin`
2. **Execute** `unifi_assign_existing_admin` with `confirm=True` (Assign an existing admin to this site. Requires confirm=True):
    - `admin`: `<admin_id_from_create>`
    - `role`: `admin`
3. **Execute** `unifi_invite_admin` with `confirm=True` (Invite an admin. Requires confirm=True):
    - `email`: `bt_sys22_invite@test.local`
    - `name`: `bt_sys22_invited`
    - `role`: `admin`
4. **Execute** `unifi_update_admin` with `confirm=True` (Update admin role. Requires confirm=True. Use _id from create step):
    - `admin`: `<admin_id_from_create>`
    - `role`: `readonly`
5. **Execute** `unifi_revoke_admin` with `confirm=True` (Revoke admin access. Requires confirm=True):
    - `admin`: `<admin_id_from_create>`
6. **Execute** `unifi_grant_super_admin` with `confirm=True` (Grant super admin. Requires confirm=True. May fail without CloudKey):
    - `admin`: `<admin_id>`
7. **Execute** `unifi_revoke_super_admin` with `confirm=True` (Revoke super admin. Requires confirm=True):
    - `admin`: `<admin_id>`
8. **Execute** `unifi_delete_admin` with `confirm=True` (Delete admin. Requires confirm=True. Run LAST.):
    - `admin`: `<admin_id_from_create>`

**Cleanup** (reverse order):
- No cleanup needed (read-only / settings restored)

**Expected outcome**: All 8 tools exercised successfully.
