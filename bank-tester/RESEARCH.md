# Bank Tester Research — Open First-Attempt Failures

**This is a living document. When a failure is fixed and verified, remove it immediately.**

**Date**: 2026-02-10
**Controller**: UniFi v10.0.162 (jacobalberty/unifi:latest, bare Docker, no adopted devices)
**Model**: Sonnet (claude -p), Opus for diagnosis
**Total tools**: 284

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
| **Fixed/restructured in Sprint E** | **4** |
| **Remaining first-attempt failures** | **34** |
| Hardware-dependent failures | 23 |
| Standalone controller limitations | 5 |
| API limitation failures | 3 |
| Test environment failures | 0 |
| Test config failures | 0 |
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

### Category: STANDALONE_LIMITATION (5 failures)

These are standalone controller limitations — not fixable via Docker seeding or generator changes. Investigated in Sprint D.

| # | Task | Tool | Error | Notes |
|---|------|------|-------|-------|
| 1 | 21 | `unifi_delete_site` | api.err.IdInvalid | Parameter format unclear |
| 2 | 21 | `unifi_delete_site` | 403 Forbidden / NoPermission | Standalone controller doesn't support site deletion even with super admin |
| 3 | 21 | `unifi_delete_site` | api.err.IdInvalid | (retry with different format) |
| 4 | 24 | `unifi_generate_backup` | api.err.NotFound | `generate-backup` command doesn't exist in cmd/backup on v10.0.162 standalone |
| 5 | 24 | `unifi_generate_backup_site` | api.err.NotFound | Same — backup generation may be UniFi OS only |

### Category: API_LIMITATION (3 failures)

Issues in the UniFi API itself on v10.0.162 — cannot fix in generator or Docker setup.

| # | Task | Tool | Error | Notes |
|---|------|------|-------|-------|
| 1 | 25 | `unifi_revoke_voucher` | api.err.NotFound | Requires hotspot portal for voucher revocation |
| 2 | 07 | `unifi_create_hotspot_package` | api.err.InvalidPayload | Requires hotspot payment gateway infrastructure |
| 3 | 19 | `unifi_create_dhcp_option` | api.err.Invalid | Requires DHCP gateway device |

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

### Sprint D: Docker Investigation (6 DOCKER_IMAGE failures)

All 6 DOCKER_IMAGE failures investigated manually against a live Docker controller. None are fixable — all are standalone controller limitations:

| Tool | Finding |
|------|---------|
| `set_site_name` | `set-site-name` command doesn't exist on v10.0.162. Tool removed (SKIP_COMMANDS). Use `update-site` instead. |
| `delete_site` (x3) | Returns NoPermission/403 even with `is_super: true` + owner role. Standalone limitation. |
| `generate_backup` | `generate-backup` command doesn't exist in `cmd/backup`. Only `list-backups` works. |
| `generate_backup_site` | Same as generate_backup. Backup generation may be UniFi OS only. |

Also fixed: MongoDB seed script privilege records used `.toString()` (returns `ObjectId("hex")`) instead of `.str` (returns `"hex"`). Added `is_super: true` to admin document.

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
| `set_site_name` | API_LIMITATION | REMOVED | Tool removed (SKIP_COMMANDS); command doesn't exist on v10.0.162 standalone |
| `delete_site` (x3) | API_LIMITATION | STANDALONE_LIMITATION | Standalone controller doesn't support site deletion |
| `generate_backup` | HARDWARE_DEPENDENT | STANDALONE_LIMITATION | Command doesn't exist in cmd/backup on standalone |
| `generate_backup_site` | HARDWARE_DEPENDENT | STANDALONE_LIMITATION | Same as generate_backup |
| `hotspot_package` | API_LIMITATION | API_LIMITATION | Confirmed by Opus: needs payment gateway |
| `dhcp_option` | API_LIMITATION | API_LIMITATION | Confirmed by Opus: needs DHCP gateway |

## Sprint E Fix Log

### Generator Fixes (1)

| Issue | Fix Applied |
|-------|-------------|
| `delete_admin` vestigial command | Added to SKIP_COMMANDS; `revoke_admin` already fully deletes admin objects |

### Test Infrastructure Fixes (3)

| Issue | Fix Applied |
|-------|-------------|
| `revoke_super_admin` CannotRevokeSelf | Restructured task 22: create 2nd admin → grant super → revoke *that* admin (not self) |
| `invite_admin` SmtpNotEnabled | Added mailpit container to docker-compose.test.yml; SMTP configured via MongoDB seed |
| `assign_existing_admin` NotFound | Restructured task 22: create 2nd site → assign existing admin across sites |

### Task Config Fixes (2)

| Issue | Fix Applied |
|-------|-------------|
| `set_site_name` referenced in task 21 | Removed (tool was already deleted in Sprint D) |
| `delete_user` generated for user CRUD | Fixed `generate-tasks.py` to respect NO_REST_DELETE |

---

## Tool Coverage

### Combined Coverage (all runs through Sprint E)

- **Smoke tests**: tasks 01, 02, 03, 08, 14, 16, 30 → ~47 unique tools
- **Full run**: tasks 04-07, 09-13, 15, 17-29 → 234 unique tools
- **Sprint A verification**: task 31 → 23 tools (14 unique new)
- **Sprint B diagnosis**: task 33 → 63 tools
- **Sprint E verification**: task 22 → 8 tools (all passed)
- **Combined unique tools invoked**: ~275/284 (~96.8%)

### Tools Never Invoked (~8)

These tools were not reachable because their create operation failed (blocking get/update/delete) or they are intentionally destructive:

**Blocked by failed create (API/hardware limitation):**
- `unifi_get/update/delete_hotspot_package` (create fails — needs payment gateway)
- `unifi_get/update/delete_dhcp_option` (create fails — needs DHCP gateway device)
- `unifi_update/delete_firewall_policy` (create fails — needs gateway + zones)
- `unifi_update_firewall_zone` (no zones exist without gateway)

**Intentionally skipped (destructive, task 99):**
- `unifi_logout`, `unifi_system_poweroff`, `unifi_system_reboot`

### Remaining Failures by Category

| Category | Count | Fixable? |
|----------|-------|----------|
| Hardware-dependent | 23 | Need adopted devices or device simulator |
| Standalone limitation | 5 | Need UniFi OS (not standalone Docker) |
| API limitation | 3 | Need payment gateway / DHCP gateway |
| Adversarial expected | 3 | By design (error quality testing) |
| **Total** | **34** | |

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
