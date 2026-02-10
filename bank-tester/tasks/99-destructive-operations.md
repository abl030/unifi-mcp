## Task 99: Destructive Operations

**task_id**: 99-destructive

**Objective**: Test destructive operations (logout, reboot, poweroff). Only run with INCLUDE_DESTRUCTIVE=1.

**Steps**:
1. **Execute** `unifi_logout` — Logs out the current session. Will break subsequent tests
2. **Execute** `unifi_system_reboot` with `confirm=True` — Reboots the controller. Wait 120s for it to come back
3. **Execute** `unifi_system_poweroff` with `confirm=True` — Powers off the controller. Container will stop

**Tools to exercise** (3):
- `unifi_logout`
- `unifi_system_reboot`
- `unifi_system_poweroff`

**Important notes**:
These will power off/reboot the controller. Only run with INCLUDE_DESTRUCTIVE=1.
The test verifies the tool triggers the action and the controller becomes unreachable.

**Cleanup**: None (controller may be unreachable after poweroff).

**Expected outcome**: Logout breaks session. Reboot makes controller temporarily unreachable. Poweroff stops the container.
