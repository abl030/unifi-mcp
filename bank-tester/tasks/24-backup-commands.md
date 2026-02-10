## Task 24: Backup Commands

**task_id**: 24-backup-commands

**Objective**: Exercise all tools in the commands subsystem.

**Tools to exercise** (5):
- `unifi_generate_backup`
- `unifi_generate_backup_site`
- `unifi_create_backup`
- `unifi_download_backup`
- `unifi_delete_backup`

**Steps**:
1. **Execute** `unifi_generate_backup` with `confirm=True` (Generate a backup. Requires confirm=True)
2. **Execute** `unifi_generate_backup_site` with `confirm=True` (Generate site-only backup. Requires confirm=True)
3. **Execute** `unifi_create_backup` with `confirm=True` (System backup command. Requires confirm=True)
4. **Execute** `unifi_download_backup` (Download a backup file. Get filename from unifi_list_backups):
    - `filename`: `<filename_from_list>`
5. **Execute** `unifi_delete_backup` with `confirm=True` (Delete backup. Requires confirm=True. Use filename from list_backups):
    - `filename`: `<filename_from_list>`

**Cleanup** (reverse order):
- No cleanup needed (read-only / settings restored)

**Expected outcome**: All 5 tools exercised successfully.
