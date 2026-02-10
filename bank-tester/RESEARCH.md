# Bank Tester Research — Open First-Attempt Failures

**This is a living document. When a failure is fixed and verified, remove it immediately.**

**Date**: 2026-02-10
**Controller**: UniFi v10.0.162 (jacobalberty/unifi:latest, bare Docker, no adopted devices)
**Model**: Sonnet (claude -p), Opus for diagnosis
**Total tools**: 285

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
| run-20260210-131059 | 33 | Sprint B: Opus diagnosis of remaining failures |

### Aggregate Numbers

| Metric | Value |
|--------|-------|
| Tasks run | 33 (of 33; task 99 destructive skipped) |
| Total tool calls | 490 |
| First-attempt failures (original) | 70 |
| **Fixed in Sprint A** | **18** |
| **Fixed/reclassified in Sprint B** | **13** |
| **Remaining first-attempt failures** | **39** |
| Hardware-dependent failures | 23 |
| Docker image fixable | 6 |
| API limitation failures | 4 |
| Test environment failures | 1 |
| Test config failures | 2 |
| Adversarial expected failures | 3 |

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

### Sprint B Results (task 33, Opus diagnosis)

Opus diagnosed all 52 remaining failures. 13 resolved, 6 reclassified:

**Confirmed WORKS (11 failures removed):**
- `block_client`, `unblock_client` — work without connected clients (Sonnet used wrong MAC flow)
- `authorize_guest`, `unauthorize_guest` — work without connected clients
- `create_user` — works with fresh MAC (previous failure was stale collision)
- `grant_super_admin` — works (Sonnet had wrong sequencing)
- `list_firewall_policies` — works (was transient startup issue)
- `unifi_self`, `sites`, `stat_sites`, `stat_admin` — work (startup race, fixed with Docker readiness delay)

**Generator fixes (2 failures fixed):**
- `delete_user` — tool removed (REST DELETE not supported; use `forget_client`)
- `create_spatial_record` — verified working with `name`, `devices: []`, `description`

**Docstring improvements (applied but failures remain hardware-dependent):**
- `create_firewall_policy` — V2_CREATE_HINTS: action, ipVersion, source, destination, schedule
- `update_traffic_route` — V2_CREATE_HINTS: targetDevices, networkId, matchingTarget

**Reclassified to DOCKER_IMAGE (6 failures moved):**
- `set_site_name` — needs enhanced MongoDB privileges
- `delete_site` (x3) — 403 Forbidden, MongoDB-seeded admin lacks auth context
- `generate_backup`, `generate_backup_site` — backup manager not initialized

---

## Every First-Attempt Failure

### Category: HARDWARE_DEPENDENT (23 failures)

These require adopted devices or connected clients. Not fixable without device simulation or real hardware.

| # | Task | Tool | Error | Notes |
|---|------|------|-------|-------|
| 1 | 12 | `unifi_list_gateway_stats` | api.err.NotFound | Needs adopted USG/UDM gateway |
| 2 | 16 | `unifi_create_firewall_policy` | HTTP 400 | Needs gateway + zones (docstring improved in Sprint B) |
| 3 | 23 | `unifi_kick_client` | api.err.UnknownStation | Needs actively connected wireless client |
| 4 | 23 | `unifi_reconnect_client` | api.err.NotFound | Needs actively connected wireless client |
| 5 | 25 | `unifi_hotspot_authorize_guest` | api.err.NotFound | Hotspot portal not configured |
| 6 | 25 | `unifi_extend_guest_validity` | api.err.NotFound | Hotspot portal not configured |
| 7 | 27 | `unifi_adopt_device` | api.err.CanNotAdoptUnknownDevice | No devices |
| 8 | 27 | `unifi_restart_device` | api.err.UnknownDevice | No devices |
| 9 | 27 | `unifi_force_provision_device` | api.err.UnknownDevice | No devices |
| 10 | 27 | `unifi_power_cycle_port` | api.err.UnknownDevice | No devices |
| 11 | 27 | `unifi_locate_device` | api.err.UnknownDevice | No devices |
| 12 | 27 | `unifi_unlocate_device` | api.err.UnknownDevice | No devices |
| 13 | 27 | `unifi_upgrade_device` | api.err.UnknownDevice | No devices |
| 14 | 27 | `unifi_upgrade_device_external` | api.err.UnknownDevice | No devices |
| 15 | 27 | `unifi_migrate_device` | api.err.UnknownDevice | No devices |
| 16 | 27 | `unifi_cancel_migrate_device` | api.err.UnknownDevice | No devices |
| 17 | 27 | `unifi_spectrum_scan` | api.err.UnknownDevice | No devices |
| 18 | 27 | `unifi_move_device` | api.err.Invalid | No devices |
| 19 | 27 | `unifi_delete_device` | api.err.UnknownDevice | No devices |
| 20 | 27 | `unifi_rename_device` | Empty result | No devices (accepted but no-op) |
| 21 | 29 | `unifi_set_port_override` | api.err.NotFound | Needs adopted device |
| 22 | 17 | `unifi_update_traffic_route` | HTTP 400 | No routes exist, needs gateway (docstring improved in Sprint B) |
| 23 | 21 | `unifi_set_site_leds` | api.err.NotFound | Needs LED-capable devices |

### Category: DOCKER_IMAGE (6 failures)

Fixable by enhancing the Docker test setup (MongoDB seeding, config changes).

| # | Task | Tool | Error | Notes |
|---|------|------|-------|-------|
| 1 | 21 | `unifi_set_site_name` | api.err.NotFound | MongoDB admin may need additional privilege records |
| 2 | 21 | `unifi_delete_site` | api.err.IdInvalid | Parameter format unclear |
| 3 | 21 | `unifi_delete_site` | 403 Forbidden | MongoDB-seeded admin lacks auth context for site deletion |
| 4 | 21 | `unifi_delete_site` | api.err.IdInvalid | (retry with different format) |
| 5 | 24 | `unifi_generate_backup` | api.err.NotFound | Backup manager not initialized in Docker |
| 6 | 24 | `unifi_generate_backup_site` | api.err.NotFound | Backup manager not initialized in Docker |

### Category: API_LIMITATION (4 failures)

Issues in the UniFi API itself on v10.0.162 — cannot fix in generator or Docker setup.

| # | Task | Tool | Error | Notes |
|---|------|------|-------|-------|
| 1 | 22 | `unifi_revoke_super_admin` | api.err.CannotRevokeSelf | Cannot revoke own super admin (safety feature) |
| 2 | 25 | `unifi_revoke_voucher` | api.err.NotFound | Requires hotspot portal for voucher revocation |
| 3 | 07 | `unifi_create_hotspot_package` | api.err.InvalidPayload | Requires hotspot payment gateway infrastructure |
| 4 | 19 | `unifi_create_dhcp_option` | api.err.Invalid | Requires DHCP gateway device |

### Category: TEST_ENV (1 failure)

| # | Task | Tool | Error | Notes |
|---|------|------|-------|-------|
| 1 | 22 | `unifi_invite_admin` | api.err.SmtpNotEnabled | No SMTP configured in Docker (UNFIXABLE) |

### Category: TEST_CONFIG (2 failures)

| # | Task | Tool | Error | Notes |
|---|------|------|-------|-------|
| 1 | 22 | `unifi_assign_existing_admin` | api.err.NotFound | Needs multi-site setup; admin already has access to only site |
| 2 | 22 | `unifi_delete_admin` | api.err.NotFound | Command broken/vestigial; use `revoke_admin` instead |

### Category: ADVERSARIAL_EXPECTED (3 failures)

Task 30 adversarial tests are DESIGNED to produce errors. These are error quality ratings, not tool failures.

| # | Task | Tool | Error Quality | Notes |
|---|------|------|---------------|-------|
| 1-4 | 30 | Various create/update/delete | missing | Generic api.err.InvalidPayload with no field detail |
| 5-6 | 30 | `update_network`, `delete_network` | unclear | api.err.IdInvalid doesn't distinguish malformed vs nonexistent |
| 7-8 | 30 | `get_setting`, `update_setting` | clear | Good error messages |

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

## Sprint B Fix Log

### Generator Fixes (3)

| Issue | Fix Applied |
|-------|-------------|
| `delete_user` REST DELETE not supported | Removed `delete_user` tool (NO_REST_DELETE set). Added workflow hint: use `forget_client`. |
| `create_firewall_policy` missing required fields | Added V2_CREATE_HINTS: action, ipVersion, source, destination, schedule |
| `update_traffic_route` missing required fields | Added V2_CREATE_HINTS: targetDevices, networkId, matchingTarget |

### Docker Fix (1)

| Issue | Fix Applied |
|-------|-------------|
| Startup race (global endpoints fail) | Added `/api/self` readiness poll in `run-bank-test.sh` after login succeeds |

### Reclassifications (Sprint B)

| Tool | Old Category | New Category | Reason |
|------|-------------|--------------|--------|
| `block_client` | HARDWARE_DEPENDENT | WORKS | Opus confirmed: works without connected client |
| `unblock_client` | HARDWARE_DEPENDENT | WORKS | Same as block_client |
| `authorize_guest` | HARDWARE_DEPENDENT | WORKS | Opus confirmed: works without connected client |
| `unauthorize_guest` | HARDWARE_DEPENDENT | WORKS | Same as authorize_guest |
| `create_user` | HARDWARE_DEPENDENT | WORKS | Opus confirmed: works with fresh MAC |
| `list_firewall_policies` | HARDWARE_DEPENDENT | WORKS | Was transient startup issue, fixed by Docker delay |
| `grant_super_admin` | API_LIMITATION | WORKS | Opus confirmed: works (Sonnet had wrong sequencing) |
| `self/sites/stat_sites/stat_admin` | TEST_ENV | WORKS | Startup race fixed by Docker readiness poll |
| `delete_user` | TEST_CONFIG | FIXED | Tool removed; use `forget_client` instead |
| `create_spatial_record` | GENERATOR_FIXABLE | VERIFIED | Opus confirmed: works with name + devices + description |
| `set_site_name` | API_LIMITATION | DOCKER_IMAGE | Needs MongoDB privilege enhancement |
| `delete_site` (x3) | API_LIMITATION | DOCKER_IMAGE | MongoDB-seeded admin lacks auth context |
| `generate_backup` | HARDWARE_DEPENDENT | DOCKER_IMAGE | Backup manager not initialized |
| `generate_backup_site` | HARDWARE_DEPENDENT | DOCKER_IMAGE | Same as generate_backup |
| `hotspot_package` | API_LIMITATION | API_LIMITATION | Confirmed by Opus: needs payment gateway |
| `dhcp_option` | API_LIMITATION | API_LIMITATION | Confirmed by Opus: needs DHCP gateway |

---

## Tool Coverage

### Combined Coverage (all runs including Sprint B)

- **Smoke tests**: tasks 01, 02, 03, 08, 14, 16, 30 → ~47 unique tools
- **Full run**: tasks 04-07, 09-13, 15, 17-29 → 234 unique tools
- **Sprint A verification**: task 31 → 23 tools (14 unique new)
- **Sprint B diagnosis**: task 33 → 63 tools
- **Combined unique tools invoked**: ~275/285 (estimated ~96.5%)

### Tools Never Invoked (estimated ~10)

These tools were not reachable because their create operation failed (blocking get/update/delete):
- `unifi_get/update/delete_hotspot_package` (create fails — API limitation)
- `unifi_get/update/delete_dhcp_option` (create fails — API limitation)
- `unifi_update/delete_firewall_policy` (create fails — hardware-dependent)
- `unifi_update_firewall_zone` (no zones exist)
- `unifi_logout`, `unifi_system_poweroff`, `unifi_system_reboot` (destructive, task 99 skipped)

---

## Observations

### What Works Well (100% first-attempt success)

Tasks 02-06, 09, 11, 13, 14, 18, 26, 28 had zero first-attempt failures:
- **REST CRUD**: network, user_group, firewall_group, firewall_rule, port_profile, port_forward, dynamic_dns, tag, account, radius_profile, wlan_group, dpi_group, dpi_app, hotspot_operator, hotspot2_config, map, schedule_task, spatial_record
- **Stats**: health, sysinfo, dashboard, country_codes, events, alarms, routing, port_forward, dynamic_dns, sdn, devices, current_channels, spectrum_scans, reporting (all 10 report tools)
- **Settings**: get_setting and update_setting work for all categories (after Sprint A fix)
- **Commands**: list_backups, get_admins, speedtest_status, check_firmware_update, clear_dpi, block_client, unblock_client, authorize_guest, unauthorize_guest, create_user, grant_super_admin (after Sprint B)

### Error Message Quality

UniFi API error codes ranked by usefulness:
- **CLEAR**: api.err.MacNotRegistered, api.err.UnknownDevice, api.err.ApGroupMissing, api.err.SmtpNotEnabled, api.err.MacAlreadyRegistered, api.err.CannotRevokeSelf, api.err.UnknownStation
- **UNCLEAR**: api.err.IdInvalid (malformed or nonexistent?), api.err.NotFound (what's missing?)
- **UNHELPFUL**: api.err.Invalid, api.err.InvalidPayload, api.err.InvalidObject (no field-level detail)

### v2 vs v1 API Differences

| Pattern | v1 REST API | v2 API |
|---------|-------------|--------|
| Partial update | Supported (send only changed fields) | Not supported (must send full object) |
| Error format | `{"meta":{"rc":"error","msg":"..."}}` | Direct HTTP status + JSON body |
| Create response | Wrapped in data array | Direct object |

The generator now documents the full-object requirement for v2 updates (Sprint A fix).
