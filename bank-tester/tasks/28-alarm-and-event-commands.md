## Task 28: Alarm and Event Commands

**task_id**: 28-alarm-and-event-commands

**Objective**: Exercise all tools in the commands subsystem.

**Tools to exercise** (2):
- `unifi_archive_alarm`
- `unifi_alarm_archive`

**Steps**:
1. **Execute** `unifi_archive_alarm` with `confirm=True` (Archive specific alarm by _id. Use a fake _id — expect graceful error):
    - `_id`: `000000000000000000000000`
2. **Execute** `unifi_alarm_archive` with `confirm=True` (Alternative alarm archive tool. Use a fake _id):
    - `_id`: `000000000000000000000000`

**Cleanup** (reverse order):
- No cleanup needed (read-only / settings restored)

**Expected outcome**: All 2 tools exercised successfully.
