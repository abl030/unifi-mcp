# Bank Tester Research — Open First-Attempt Failures

**This is a living document. When a failure is fixed and verified, remove it immediately.**

**Date**: 2026-02-10
**Controller**: UniFi v10.0.162 (jacobalberty/unifi:latest, bare Docker, no adopted devices)
**Model**: Sonnet (claude -p)
**Total tools**: 286

## Combined Results (All Runs)

### Runs Analyzed

| Run | Tasks | Description |
|-----|-------|-------------|
| run-20260210-105234 | 01 | Smoke: global endpoints |
| run-20260210-105353 | 02 | Smoke: network + user group CRUD |
| run-20260210-105521 | 03 | Smoke: firewall groups + rules CRUD |
| run-20260210-105651 | 08 | Smoke: safe commands |
| run-20260210-105804 | 14 | Smoke: settings read |
| run-20260210-105954 | 16 | Smoke: v2 firewall policies + zones |
| run-20260210-114547 | 30 | Smoke: adversarial tests (post error-handling fix) |
| run-20260210-114955 | 04-07, 09-13, 15, 17-29 | Full run: all remaining tasks |
| run-20260210-125339 | 31 | Sprint A verification: generator fixes |

### Aggregate Numbers

| Metric | Value |
|--------|-------|
| Tasks run | 31 (of 31; task 99 destructive skipped) |
| Total tool calls | 428 |
| First-attempt failures (original) | 70 |
| **Fixed in Sprint A** | **18** |
| **Remaining first-attempt failures** | **52** |
| Hardware-dependent failures | 31 |
| API limitation failures | 9 (7 original + 2 reclassified) |
| Test environment failures | 5 |
| Test config failures | 3 |
| Adversarial expected failures | 3 |
| Generator-fixable remaining | 1 (spatialrecord, fix verified but needs re-test) |

### Sprint A Results (task 31)

18 of 21 generator-fixable failures verified fixed:
- Settings endpoint routing (set/setting/{key}): 6/6 fixed
- stat/session POST body defaults: 1/1 fixed
- Heatmap + heatmap_point required fields: 2/2 fixed
- Schedule task full-object docstring: 1/1 fixed
- Traffic rule enum values + full-object docstring: 2/2 fixed
- clear_dpi command mapping (reset-dpi): 1/1 fixed
- MAC address client-side validation: 1/1 fixed
- update_map type confusion: 1/1 fixed (not reproduced)
- 2 reclassified to API_LIMITATION (hotspotpackage, dhcpoption)
- 1 fixed post-verification (spatialrecord needs `devices: []`)

---

## Every First-Attempt Failure

### Category: HARDWARE_DEPENDENT (31 failures)

These are expected on a bare controller with no adopted devices or connected clients. Not fixable without device simulation or real hardware.

| # | Task | Tool | Error | Notes |
|---|------|------|-------|-------|
| 1 | 12 | `unifi_list_gateway_stats` | api.err.NotFound | Needs adopted USG/UDM gateway |
| 2 | 16 | `unifi_create_firewall_policy` | HTTP 400 | v2 firewall needs gateway + zones |
| 3 | 16 | `unifi_list_firewall_policies` | JSON parse error | Transient startup issue |
| 4 | 23 | `unifi_block_client` | api.err.MacNotRegistered | Needs connected client |
| 5 | 23 | `unifi_unblock_client` | api.err.MacNotRegistered | Needs connected client |
| 6 | 23 | `unifi_kick_client` | api.err.MacNotRegistered | Needs connected client |
| 7 | 23 | `unifi_reconnect_client` | api.err.MacNotRegistered | Needs connected client |
| 8 | 23 | `unifi_authorize_guest` | api.err.MacNotRegistered | Needs connected client |
| 9 | 23 | `unifi_unauthorize_guest` | api.err.MacNotRegistered | Needs connected client |
| 10 | 24 | `unifi_generate_backup` | api.err.NotFound | cmd/backup manager missing on v10.0.162 |
| 11 | 24 | `unifi_generate_backup_site` | api.err.NotFound | cmd/backup manager missing on v10.0.162 |
| 12 | 25 | `unifi_hotspot_authorize_guest` | api.err.NotFound | Hotspot feature not enabled |
| 13 | 25 | `unifi_extend_guest_validity` | api.err.NotFound | Hotspot feature not enabled |
| 14 | 27 | `unifi_adopt_device` | api.err.CanNotAdoptUnknownDevice | No devices |
| 15 | 27 | `unifi_restart_device` | api.err.UnknownDevice | No devices |
| 16 | 27 | `unifi_force_provision_device` | api.err.UnknownDevice | No devices |
| 17 | 27 | `unifi_power_cycle_port` | api.err.UnknownDevice | No devices |
| 18 | 27 | `unifi_locate_device` | api.err.UnknownDevice | No devices |
| 19 | 27 | `unifi_unlocate_device` | api.err.UnknownDevice | No devices |
| 20 | 27 | `unifi_upgrade_device` | api.err.UnknownDevice | No devices |
| 21 | 27 | `unifi_upgrade_device_external` | api.err.UnknownDevice | No devices |
| 22 | 27 | `unifi_migrate_device` | api.err.UnknownDevice | No devices |
| 23 | 27 | `unifi_cancel_migrate_device` | api.err.UnknownDevice | No devices |
| 24 | 27 | `unifi_spectrum_scan` | api.err.UnknownDevice | No devices |
| 25 | 27 | `unifi_move_device` | api.err.Invalid | No devices |
| 26 | 27 | `unifi_delete_device` | api.err.UnknownDevice | No devices |
| 27 | 27 | `unifi_rename_device` | Empty result | No devices (accepted but no-op) |
| 28 | 29 | `unifi_set_port_override` | api.err.NotFound | Needs adopted device |
| 29 | 17 | `unifi_update_traffic_route` | HTTP 400 | No routes exist (needs gateway) |
| 30 | 21 | `unifi_set_site_leds` | api.err.NotFound | Needs LED-capable devices |
| 31 | 23 | `unifi_create_user` | api.err.MacAlreadyRegistered | Stale data from previous test run |

### Category: API_LIMITATION (9 failures)

Issues in the UniFi API itself on v10.0.162 — cannot fix in generator.

| # | Task | Tool | Error | Notes |
|---|------|------|-------|-------|
| 1 | 21 | `unifi_set_site_name` | api.err.NotFound | Command may not exist on v10.0.162 |
| 2 | 21 | `unifi_delete_site` | api.err.IdInvalid | Parameter format unclear; tried name, _id, desc — all fail |
| 3 | 21 | `unifi_delete_site` | 403 Forbidden | Permissions issue, test admin can't delete sites |
| 4 | 21 | `unifi_delete_site` | api.err.IdInvalid | (retry with different format) |
| 5 | 22 | `unifi_grant_super_admin` | api.err.InvalidTarget | May need CloudKey/UniFi OS |
| 6 | 22 | `unifi_revoke_super_admin` | api.err.InvalidTarget | Can't revoke what wasn't granted |
| 7 | 25 | `unifi_revoke_voucher` | api.err.NotFound | Inconsistent: create/delete work, revoke doesn't |
| 8 | 07 | `unifi_create_hotspot_package` | api.err.InvalidHotspotPackageDuration | Requires hotspot payment gateway infrastructure (probed: all field combos rejected) |
| 9 | 19 | `unifi_create_dhcp_option` | api.err.Invalid | Requires DHCP gateway device (probed: code validation passes but create always fails) |

### Category: TEST_ENV (5 failures)

Issues with the bare test environment setup.

| # | Task | Tool | Error | Notes |
|---|------|------|-------|-------|
| 1-4 | 01 | `unifi_self`, `sites`, `stat_sites`, `stat_admin` | JSON parse error | Startup race: auth not ready when /status returns 200 |
| 5 | 22 | `unifi_invite_admin` | api.err.SmtpNotEnabled | No SMTP configured in Docker |

### Category: TEST_CONFIG (3 failures)

Task specification or test value issues.

| # | Task | Tool | Error | Notes |
|---|------|------|-------|-------|
| 1 | 22 | `unifi_assign_existing_admin` | api.err.NotFound | Command purpose unclear; test expectations may be wrong |
| 2 | 22 | `unifi_delete_admin` | api.err.NotFound | Admin already deleted by revoke_admin (unexpected side effect) |
| 3 | 29 | `unifi_delete_user` | api.err.NotFound | REST DELETE may not be supported for user resource |

### Category: ADVERSARIAL_EXPECTED (3 failures)

Task 30 adversarial tests are DESIGNED to produce errors. These are error quality ratings, not tool failures.

| # | Task | Tool | Error Quality | Notes |
|---|------|------|---------------|-------|
| 1-4 | 30 | Various create/update/delete | missing | Generic api.err.InvalidPayload with no field detail |
| 5-6 | 30 | `update_network`, `delete_network` | unclear | api.err.IdInvalid doesn't distinguish malformed vs nonexistent |
| 7-8 | 30 | `get_setting`, `update_setting` | clear | Good error messages |

### Category: GENERATOR_FIXABLE (1 remaining)

| # | Task | Tool | Error | Status |
|---|------|------|-------|--------|
| 1 | 20 | `unifi_create_spatial_record` | api.err.Invalid | Fixed: needs `devices: []` array. Awaiting re-verification. |

---

## Sprint A Fix Log

### Verified Fixed (18 failures eliminated)

| Issue | Failures Fixed | Fix Applied |
|-------|---------------|-------------|
| update_setting wrong endpoint | 6 | Changed to `PUT set/setting/{key}` instead of `PUT rest/setting/{id}` |
| list_sessions missing POST body | 1 | STAT_OVERRIDES body: `{"type":"all","start":0,"end":9999999999}` + template uses `tool.post_body` |
| create_heatmap undocumented fields | 1 | Added REQUIRED_CREATE_FIELDS: `name`, `map_id` |
| create_heatmap_point undocumented fields | 1 | Added REQUIRED_CREATE_FIELDS: `heatmap_id`, `x`, `y` |
| update_schedule_task full object | 1 | Added FULL_OBJECT_UPDATE_REST docstring note |
| update_map type confusion | 1 | Not reproduced in verification test |
| create_traffic_rule missing enums | 1 | Added V2_CREATE_HINTS with target_devices[].type values |
| update_traffic_rule full object | 1 | Added v2 update docstring: "full object required" |
| update_traffic_route full object | 1 | Same v2 update docstring (hardware-dep, verified separately) |
| clear_dpi wrong command | 1 | Renamed `clear-dpi` to `reset-dpi` |
| block_client no MAC validation | 1 | Added `_validate_mac()` helper + calls in all stamgr commands |

### Reclassified (3 failures moved from GENERATOR_FIXABLE)

| Tool | Old Category | New Category | Reason |
|------|-------------|--------------|--------|
| `unifi_create_hotspot_package` | GENERATOR_FIXABLE | API_LIMITATION | Probed all field combos — always fails with InvalidHotspotPackageDuration. Needs payment gateway infrastructure. |
| `unifi_create_dhcp_option` | GENERATOR_FIXABLE | API_LIMITATION | Probed many field combos — code validation works but create always fails. Needs DHCP gateway device. |
| `unifi_create_spatial_record` | GENERATOR_FIXABLE | GENERATOR_FIXABLE | Fixed: needs `devices: []`. Awaiting re-verification. |

---

## Tool Coverage

### Combined Coverage (all runs including Sprint A verification)

- **Smoke tests**: tasks 01, 02, 03, 08, 14, 16, 30 → ~47 unique tools
- **Full run**: tasks 04-07, 09-13, 15, 17-29 → 234 unique tools
- **Sprint A verification**: task 31 → 23 tools (14 unique new)
- **Combined unique tools invoked**: ~270/286 (estimated ~94.4%)

### Tools Never Invoked (estimated ~16)

These tools were not reachable because their create operation failed (blocking get/update/delete):
- `unifi_get/update/delete_hotspot_package` (create fails — API limitation)
- `unifi_get/update/delete_dhcp_option` (create fails — API limitation)
- `unifi_get/update/delete_spatial_record` (create fails — fix pending verification)
- `unifi_update/delete_firewall_policy` (create fails — hardware-dependent)
- `unifi_update_firewall_zone` (no zones exist)
- `unifi_logout`, `unifi_system_poweroff`, `unifi_system_reboot` (destructive, task 99 skipped)

---

## Observations

### What Works Well (100% first-attempt success)

Tasks 02-06, 09, 11, 13, 14, 18, 26, 28 had zero first-attempt failures:
- **REST CRUD**: network, user_group, firewall_group, firewall_rule, port_profile, port_forward, dynamic_dns, tag, account, radius_profile, wlan_group, dpi_group, dpi_app, hotspot_operator, hotspot2_config, map, schedule_task
- **Stats**: health, sysinfo, dashboard, country_codes, events, alarms, routing, port_forward, dynamic_dns, sdn, devices, current_channels, spectrum_scans, reporting (all 10 report tools)
- **Settings**: get_setting and update_setting work for all categories (after Sprint A fix)
- **Commands**: list_backups, get_admins, speedtest_status, check_firmware_update, clear_dpi (after Sprint A fix)

### Error Message Quality

UniFi API error codes ranked by usefulness:
- **CLEAR**: api.err.MacNotRegistered, api.err.UnknownDevice, api.err.ApGroupMissing, api.err.SmtpNotEnabled, api.err.MacAlreadyRegistered
- **UNCLEAR**: api.err.IdInvalid (malformed or nonexistent?), api.err.NotFound (what's missing?)
- **UNHELPFUL**: api.err.Invalid, api.err.InvalidPayload, api.err.InvalidObject (no field-level detail)

### v2 vs v1 API Differences

| Pattern | v1 REST API | v2 API |
|---------|-------------|--------|
| Partial update | Supported (send only changed fields) | Not supported (must send full object) |
| Error format | `{"meta":{"rc":"error","msg":"..."}}` | Direct HTTP status + JSON body |
| Create response | Wrapped in data array | Direct object |

The generator now documents the full-object requirement for v2 updates (Sprint A fix).
