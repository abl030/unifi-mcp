## Task 21: Site Management Commands

**task_id**: 21-site-management-commands

**Objective**: Exercise all tools in the commands subsystem.

**Tools to exercise** (5):
- `unifi_add_site`
- `unifi_set_site_name`
- `unifi_set_site_leds`
- `unifi_update_site`
- `unifi_delete_site`

**Steps**:
1. **Execute** `unifi_add_site` with `confirm=True` (Creates a new site. Requires confirm=True):
    - `desc`: `bt_sys21_site`
2. **Execute** `unifi_set_site_name` with `confirm=True` (Renames current site. Requires confirm=True):
    - `desc`: `bt_sys21_renamed`
3. **Execute** `unifi_set_site_leds` with `confirm=True` (Enable/disable site LEDs. Requires confirm=True):
    - `led_enabled`: `True`
4. **Execute** `unifi_update_site` with `confirm=True` (Update site description. Requires confirm=True):
    - `desc`: `bt_sys21_updated`
5. **Execute** `unifi_delete_site` with `confirm=True` (Delete the site created above. Requires confirm=True. Run LAST.):
    - `site`: `bt_sys21_site`

**Cleanup** (reverse order):
- No cleanup needed (read-only / settings restored)

**Expected outcome**: All 5 tools exercised successfully.
