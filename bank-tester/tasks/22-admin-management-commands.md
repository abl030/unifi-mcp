## Task 22: Admin Management Commands

**task_id**: 22-admin-management-commands

**Objective**: Exercise all tools in the commands subsystem.

**Tools to exercise** (8):
- `unifi_create_admin`
- `unifi_add_site`
- `unifi_assign_existing_admin`
- `unifi_invite_admin`
- `unifi_update_admin`
- `unifi_grant_super_admin`
- `unifi_revoke_super_admin`
- `unifi_revoke_admin`

**Steps**:
1. **Execute** `unifi_create_admin` with `confirm=True` (Creates a new admin. Save the returned _id as <admin_id>. Requires confirm=True):
    - `name`: `bt_sys22_admin`
    - `email`: `bt_sys22@test.local`
    - `x_password`: `TestPassword123!`
    - `role`: `admin`
2. **Execute** `unifi_add_site` with `confirm=True` (Create a second site for the assign_existing_admin test. Requires confirm=True):
    - `desc`: `bt_sys22_site`
3. **Execute** `unifi_assign_existing_admin` with `confirm=True` (Assign the admin created in step 1 to bt_sys22_site. Use site='bt_sys22_site'. Requires confirm=True):
    - `admin`: `<admin_id>`
    - `role`: `admin`
4. **Execute** `unifi_invite_admin` with `confirm=True` (Invite an admin via email. SMTP is configured (mailpit). Requires confirm=True):
    - `email`: `bt_sys22_invite@test.local`
    - `name`: `bt_sys22_invited`
    - `role`: `admin`
5. **Execute** `unifi_update_admin` with `confirm=True` (Update admin role. Use _id from step 1. Requires confirm=True):
    - `admin`: `<admin_id>`
    - `role`: `readonly`
6. **Execute** `unifi_grant_super_admin` with `confirm=True` (Grant super admin to the admin from step 1 (NOT yourself). Requires confirm=True):
    - `admin`: `<admin_id>`
7. **Execute** `unifi_revoke_super_admin` with `confirm=True` (Revoke super admin from the admin from step 1 (NOT yourself — revoking self will fail with CannotRevokeSelf). Requires confirm=True):
    - `admin`: `<admin_id>`
8. **Execute** `unifi_revoke_admin` with `confirm=True` (Revoke admin access. This fully deletes the admin object. Requires confirm=True. Run LAST.):
    - `admin`: `<admin_id>`

**Cleanup** (reverse order):
- No cleanup needed (read-only / settings restored)

**Expected outcome**: All 8 tools exercised successfully.
