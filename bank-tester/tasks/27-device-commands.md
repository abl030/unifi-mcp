## Task 27: Device Commands

**task_id**: 27-device-commands

**Objective**: Exercise all tools in the commands subsystem.

**Tools to exercise** (29):
- `unifi_adopt_device`
- `unifi_restart_device`
- `unifi_force_provision_device`
- `unifi_power_cycle_port`
- `unifi_run_speedtest`
- `unifi_locate_device`
- `unifi_unlocate_device`
- `unifi_upgrade_device`
- `unifi_upgrade_device_external`
- `unifi_migrate_device`
- `unifi_cancel_migrate_device`
- `unifi_spectrum_scan`
- `unifi_rename_device`
- `unifi_led_override_device`
- `unifi_disable_ap`
- `unifi_rolling_upgrade`
- `unifi_cancel_rolling_upgrade`
- `unifi_upgrade_all_devices`
- `unifi_advanced_adopt_device`
- `unifi_set_rollupgrade`
- `unifi_unset_rollupgrade`
- `unifi_enable_device`
- `unifi_disable_device`
- `unifi_cable_test`
- `unifi_set_inform_device`
- `unifi_move_device`
- `unifi_delete_device`
- `unifi_element_adoption`
- `unifi_reboot_cloudkey`

**Steps**:
1. **Execute** `unifi_adopt_device` with `confirm=True` **[Hardware-dependent — expect error]**:
    - `mac`: `00:00:00:00:00:01`
2. **Execute** `unifi_restart_device` with `confirm=True` **[Hardware-dependent — expect error]**:
    - `mac`: `00:00:00:00:00:01`
3. **Execute** `unifi_force_provision_device` with `confirm=True` **[Hardware-dependent — expect error]**:
    - `mac`: `00:00:00:00:00:01`
4. **Execute** `unifi_power_cycle_port` with `confirm=True` **[Hardware-dependent — expect error]**:
    - `mac`: `00:00:00:00:00:01`
    - `port_idx`: `1`
5. **Execute** `unifi_run_speedtest` with `confirm=True` **[Hardware-dependent — expect error]**
6. **Execute** `unifi_locate_device` with `confirm=True` **[Hardware-dependent — expect error]**:
    - `mac`: `00:00:00:00:00:01`
7. **Execute** `unifi_unlocate_device` with `confirm=True` **[Hardware-dependent — expect error]**:
    - `mac`: `00:00:00:00:00:01`
8. **Execute** `unifi_upgrade_device` with `confirm=True` **[Hardware-dependent — expect error]**:
    - `mac`: `00:00:00:00:00:01`
9. **Execute** `unifi_upgrade_device_external` with `confirm=True` **[Hardware-dependent — expect error]**:
    - `mac`: `00:00:00:00:00:01`
    - `url`: `https://example.com/firmware.bin`
10. **Execute** `unifi_migrate_device` with `confirm=True` **[Hardware-dependent — expect error]**:
    - `mac`: `00:00:00:00:00:01`
    - `inform_url`: `http://192.168.1.1:8080/inform`
11. **Execute** `unifi_cancel_migrate_device` with `confirm=True` **[Hardware-dependent — expect error]**:
    - `mac`: `00:00:00:00:00:01`
12. **Execute** `unifi_spectrum_scan` with `confirm=True` **[Hardware-dependent — expect error]**:
    - `mac`: `00:00:00:00:00:01`
13. **Execute** `unifi_rename_device` with `confirm=True` **[Hardware-dependent — expect error]**:
    - `mac`: `00:00:00:00:00:01`
    - `name`: `bt_sys27_device`
14. **Execute** `unifi_led_override_device` with `confirm=True` **[Hardware-dependent — expect error]**:
    - `mac`: `00:00:00:00:00:01`
    - `led_override`: `on`
15. **Execute** `unifi_disable_ap` with `confirm=True` **[Hardware-dependent — expect error]**:
    - `mac`: `00:00:00:00:00:01`
16. **Execute** `unifi_rolling_upgrade` with `confirm=True` **[Hardware-dependent — expect error]**
17. **Execute** `unifi_cancel_rolling_upgrade` with `confirm=True` **[Hardware-dependent — expect error]**
18. **Execute** `unifi_upgrade_all_devices` with `confirm=True` **[Hardware-dependent — expect error]**
19. **Execute** `unifi_advanced_adopt_device` with `confirm=True` **[Hardware-dependent — expect error]**:
    - `mac`: `00:00:00:00:00:01`
    - `url`: `http://192.168.1.1:8080/inform`
    - `key`: `testkey123`
20. **Execute** `unifi_set_rollupgrade` with `confirm=True` **[Hardware-dependent — expect error]**:
    - `mac`: `00:00:00:00:00:01`
21. **Execute** `unifi_unset_rollupgrade` with `confirm=True` **[Hardware-dependent — expect error]**:
    - `mac`: `00:00:00:00:00:01`
22. **Execute** `unifi_enable_device` with `confirm=True` **[Hardware-dependent — expect error]**:
    - `mac`: `00:00:00:00:00:01`
23. **Execute** `unifi_disable_device` with `confirm=True` **[Hardware-dependent — expect error]**:
    - `mac`: `00:00:00:00:00:01`
24. **Execute** `unifi_cable_test` with `confirm=True` **[Hardware-dependent — expect error]**:
    - `mac`: `00:00:00:00:00:01`
    - `port_idx`: `1`
25. **Execute** `unifi_set_inform_device` with `confirm=True` **[Hardware-dependent — expect error]**:
    - `mac`: `00:00:00:00:00:01`
    - `inform_url`: `http://192.168.1.1:8080/inform`
26. **Execute** `unifi_move_device` with `confirm=True` **[Hardware-dependent — expect error]**:
    - `mac`: `00:00:00:00:00:01`
    - `site`: `default`
27. **Execute** `unifi_delete_device` with `confirm=True` **[Hardware-dependent — expect error]**:
    - `mac`: `00:00:00:00:00:01`
28. **Execute** `unifi_element_adoption` with `confirm=True` **[Hardware-dependent — expect error]**:
    - `mac`: `00:00:00:00:00:01`
29. **Execute** `unifi_reboot_cloudkey` with `confirm=True` **[Hardware-dependent — expect error]** (May fail on standalone controller (not CloudKey))

**Important notes**:
These commands require adopted devices. Expect errors about missing devices.
The test verifies the tool exists and returns sensible errors.

**Cleanup** (reverse order):
- No cleanup needed (read-only / settings restored)

**Expected outcome**: All 29 tools exercised successfully.
