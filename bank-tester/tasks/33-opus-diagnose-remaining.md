## Task 33: Opus Diagnosis of Remaining Failures

**task_id**: 33-opus-diagnose-remaining

**Objective**: Diagnose all 52 remaining first-attempt failures from the Sonnet bank test. For each failure, attempt the call, try alternative approaches, diagnose the root cause, and recommend a fix category. You are a senior QA engineer — go deeper than the previous tester. Try creative alternatives.

**Fix Categories** (use exactly one per failure in your report):
- `DOCKER_IMAGE` — Fixable by enhancing the Docker test setup (MongoDB seeding, config changes, enabling features)
- `GENERATOR` — Fixable by changing the MCP tool generator (docstrings, params, endpoint)
- `UNFIXABLE` — True API limitation or requires physical hardware; accept and document

---

### Section 1: Verify Spatialrecord Fix (1 generator-fixable remaining)

The generator was updated to document required fields: `name`, `devices`, `description`. Verify the fix works.

**Step 1.1**: Create a map first (needed as context):
- `unifi_create_map` with `name="bt_diag_map"`, `confirm=True`

**Step 1.2**: Create spatial record with the documented fields:
- `unifi_create_spatial_record` with `name="bt_diag_spatial"`, `devices=[]`, `description="Diagnosis test"`, `confirm=True`
- Previous Sonnet error: `api.err.Invalid` (missing required fields)
- If this succeeds, the generator fix is verified

**Step 1.3**: Cleanup — delete the spatial record and map

---

### Section 2: Test Environment (5 failures)

These failed due to startup race conditions or missing services.

**Step 2.1**: Global endpoints (previously: JSON parse error from startup race)
- `unifi_self` — GET /api/self
- `unifi_list_sites` — GET /api/self/sites
- `unifi_list_stat_sites` — GET /api/stat/sites
- `unifi_list_stat_admin` — GET /api/stat/admin
- Previous error: JSON parse error (auth not ready when /status returns 200)
- **Diagnosis goal**: Do these work now (later in the controller's lifecycle)? If yes → `DOCKER_IMAGE` fix (extend startup wait). If no → investigate further.

**Step 2.2**: Invite admin (previously: SMTP not enabled)
- `unifi_invite_admin` with `name="bt_diag_invite"`, `email="diag@test.local"`, `confirm=True`
- Previous error: `api.err.SmtpNotEnabled`
- **Try**: Is there a way to invite without SMTP? Different params? Role-only invite?

---

### Section 3: Test Config (3 failures)

These may be task specification issues rather than tool issues.

**Step 3.1**: Assign existing admin
- First, call `unifi_get_admins` to list current admins and get an admin `_id`
- Then try `unifi_assign_existing_admin` with the admin's `_id`, `confirm=True`
- Previous error: `api.err.NotFound`
- **Try**: Different param names (`admin_id`, `_id`), different values. What does this command actually expect?

**Step 3.2**: Delete admin
- First, call `unifi_get_admins` to list admins
- Then try `unifi_delete_admin` — what params does it expect?
- Previous error: `api.err.NotFound` (admin already deleted by revoke_admin side effect)
- **Try**: Create a fresh admin via `unifi_create_admin`, then delete it

**Step 3.3**: Delete user
- First, call `unifi_list_users` to find any existing users
- Then try `unifi_delete_user` with a valid user `_id`, `confirm=True`
- Previous error: `api.err.NotFound`
- **Try**: Create a user first via `unifi_create_user` with a fresh MAC (e.g. `00:11:22:33:44:55`), then delete. Does REST DELETE work for users, or is there a different mechanism?

---

### Section 4: API Limitation (9 failures)

These appear to be UniFi API limitations. Verify each and confirm whether they're truly unfixable.

**Step 4.1**: Set site name
- `unifi_set_site_name` with `name="bt_diag_site"`, `confirm=True`
- Previous error: `api.err.NotFound`
- **Try**: Different param format. Does the command exist on v10.0.162? Check the docstring for expected params.

**Step 4.2**: Delete site
- First, create a test site: `unifi_create_site` with `name="bt_diag_delsite"`, `confirm=True`
- Then try `unifi_delete_site` with the site `_id` from the create response, `confirm=True`
- Previous errors: `api.err.IdInvalid`, `403 Forbidden`
- **Try**: Use `name` instead of `_id`. Use `desc` field. Try the site name string.

**Step 4.3**: Grant/revoke super admin
- Call `unifi_get_admins` to get admin `_id`
- `unifi_grant_super_admin` with admin `_id`, `confirm=True`
- Previous error: `api.err.InvalidTarget`
- **Try**: Different target format. Does this need CloudKey/UniFi OS?
- Then try `unifi_revoke_super_admin` with same `_id`, `confirm=True`

**Step 4.4**: Revoke voucher
- First, create a voucher: `unifi_create_voucher` with `n=1`, `confirm=True`
- Note the voucher `_id` from the create response
- Then try `unifi_revoke_voucher` with that `_id`, `confirm=True`
- Previous error: `api.err.NotFound`
- **Try**: Different param names. Is `_id` the right identifier? Check the docstring.

**Step 4.5**: Create hotspot package (reclassified from generator-fixable)
- `unifi_create_hotspot_package` with `name="bt_diag_pkg"`, `amount=0`, `currency="USD"`, `hours=1`, `bytes=0`, `confirm=True`
- Previous error: `api.err.InvalidHotspotPackageDuration`
- **Try**: Add `duration` param. Try `hours` as string. Try `minutes` field. Read the docstring carefully.

**Step 4.6**: Create DHCP option (reclassified from generator-fixable)
- `unifi_create_dhcp_option` with `name="bt_diag_dhcp"`, `code=100`, `value="test"`, `confirm=True`
- Previous error: `api.err.Invalid`
- **Try**: Different code numbers (66, 67 are standard DHCP options). Try with `enabled=True`. Read the docstring.

---

### Section 5: Hardware-Dependent (31 failures)

These fail because no devices are adopted in the Docker controller. For each, try the call and assess whether the error message clearly indicates a hardware dependency, or if there might be a workaround.

**Important**: For device commands (adopt, restart, etc.), you'll need a MAC address. Use `AA:BB:CC:DD:EE:FF` as a test MAC. For client commands, use `00:11:22:33:44:55`.

#### 5A: Client commands (Task 23 — 7 failures)

For each, use MAC `00:11:22:33:44:55`:
- `unifi_block_client` with `mac="00:11:22:33:44:55"`, `confirm=True`
- `unifi_unblock_client` with `mac="00:11:22:33:44:55"`, `confirm=True`
- `unifi_kick_client` with `mac="00:11:22:33:44:55"`, `confirm=True`
- `unifi_reconnect_client` with `mac="00:11:22:33:44:55"`, `confirm=True`
- `unifi_authorize_guest` with `mac="00:11:22:33:44:55"`, `confirm=True`
- `unifi_unauthorize_guest` with `mac="00:11:22:33:44:55"`, `confirm=True`
- `unifi_create_user` with `mac="00:11:22:33:44:56"`, `confirm=True` (fresh MAC to avoid collision)

Previous errors: `api.err.MacNotRegistered` (client commands), `api.err.MacAlreadyRegistered` (create_user)

**Diagnosis goal**: Can `create_user` work with a truly fresh MAC? For block/unblock/kick, is `MacNotRegistered` the expected error without a connected client?

#### 5B: Device commands (Task 27 — 14 failures)

For each, use MAC `AA:BB:CC:DD:EE:FF`:
- `unifi_adopt_device` with `mac="AA:BB:CC:DD:EE:FF"`, `confirm=True`
- `unifi_restart_device` with `mac="AA:BB:CC:DD:EE:FF"`, `confirm=True`
- `unifi_force_provision_device` with `mac="AA:BB:CC:DD:EE:FF"`, `confirm=True`
- `unifi_power_cycle_port` with `mac="AA:BB:CC:DD:EE:FF"`, `port_idx=1`, `confirm=True`
- `unifi_locate_device` with `mac="AA:BB:CC:DD:EE:FF"`, `confirm=True`
- `unifi_unlocate_device` with `mac="AA:BB:CC:DD:EE:FF"`, `confirm=True`
- `unifi_upgrade_device` with `mac="AA:BB:CC:DD:EE:FF"`, `confirm=True`
- `unifi_upgrade_device_external` with `mac="AA:BB:CC:DD:EE:FF"`, `url="http://example.com/fw.bin"`, `confirm=True`
- `unifi_migrate_device` with `mac="AA:BB:CC:DD:EE:FF"`, `inform_url="http://localhost:8080/inform"`, `confirm=True`
- `unifi_cancel_migrate_device` with `mac="AA:BB:CC:DD:EE:FF"`, `confirm=True`
- `unifi_spectrum_scan` with `mac="AA:BB:CC:DD:EE:FF"`, `confirm=True`
- `unifi_move_device` with `mac="AA:BB:CC:DD:EE:FF"`, `site="default"`, `confirm=True`
- `unifi_delete_device` with `mac="AA:BB:CC:DD:EE:FF"`, `confirm=True`
- `unifi_rename_device` with `mac="AA:BB:CC:DD:EE:FF"`, `name="bt_diag_device"`, `confirm=True`

Previous errors: `api.err.UnknownDevice`, `api.err.CanNotAdoptUnknownDevice`, `api.err.Invalid`, empty result

**Diagnosis goal**: Confirm these all require physical/adopted devices. Can any be tricked with a seeded MAC in MongoDB?

#### 5C: Other hardware-dependent (10 failures)

- `unifi_list_gateway_stats` — Previous: `api.err.NotFound`. Needs USG/UDM gateway.
- `unifi_create_firewall_policy` — Try with `name="bt_diag_policy"`, `enabled=True`, `confirm=True`. Previous: HTTP 400. Check the docstring for required params.
- `unifi_list_firewall_policies` — Previous: JSON parse error (transient?). Just call it.
- `unifi_set_port_override` — Try with `device_id="nonexistent"`, `port_idx=1`, `portconf_id="test"`, `confirm=True`. Previous: `api.err.NotFound`.
- `unifi_update_traffic_route` — Previous: HTTP 400. Need to list routes first: `unifi_list_traffic_routes`, then try update if any exist.
- `unifi_set_site_leds` with `enabled=True`, `confirm=True` — Previous: `api.err.NotFound`. Does this command exist on v10.0.162?
- `unifi_generate_backup` with `confirm=True` — Previous: `api.err.NotFound`. Does backup command exist?
- `unifi_generate_backup_site` with `confirm=True` — Previous: `api.err.NotFound`. Same as above.
- `unifi_hotspot_authorize_guest` with `mac="00:11:22:33:44:55"`, `confirm=True` — Previous: `api.err.NotFound`. Hotspot feature?
- `unifi_extend_guest_validity` with `id="nonexistent"`, `confirm=True` — Previous: `api.err.NotFound`. Hotspot feature?

---

### Section 6: Adversarial Expected (3 failures)

These are from Task 30 (error quality testing). They are EXPECTED failures — the goal is to assess error message quality, not fix them.

- Try `unifi_create_network` with empty `data={}`, `confirm=True` — rate the error message
- Try `unifi_update_network` with `_id="nonexistent_id_12345"`, `data={"name":"x"}`, `confirm=True` — rate the error
- Try `unifi_delete_network` with `_id="nonexistent_id_12345"`, `confirm=True` — rate the error

Rate each as `clear`, `unclear`, or `missing` (same as Task 30).

---

### Cleanup

Delete any resources you created during diagnosis (maps, spatial records, sites, users, vouchers, etc.) in reverse order.

---

### Report Format

Use the standard TASK-REPORT format but add a `fix_category` field to each detail entry:

```
---TASK-REPORT-START---
task_id: 33-opus-diagnose-remaining
status: partial
total_tool_calls: <number>
first_attempt_failures: <number>
details:
  - tool: <tool_name>
    attempt: 1
    params: <what you sent>
    error: <error message received>
    diagnosis: <your detailed analysis — what causes this, what would fix it>
    fix_category: DOCKER_IMAGE | GENERATOR | UNFIXABLE
    alternative_tried: <what alternative you tried, if any>
    alternative_result: <result of alternative approach>
cleanup_complete: true | false
notes: |
  <Overall summary of findings. Group by fix_category.
   For DOCKER_IMAGE: what specific Docker/MongoDB changes are needed?
   For GENERATOR: what specific generator changes are needed?
   For UNFIXABLE: why is it unfixable?>
tools_invoked:
  - <tool_name_1>
  - <tool_name_2>
  - ...
---TASK-REPORT-END---
```

**IMPORTANT**: Include EVERY tool you called in `tools_invoked`. Include the `fix_category` for EVERY failure in `details`. The `diagnosis` field is the most valuable output — be specific about root causes and concrete fix recommendations.
