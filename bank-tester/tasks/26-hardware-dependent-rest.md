## Task 26: Hardware-Dependent REST

**task_id**: 26-hardware-dependent-rest

**Objective**: Exercise all tools in the hardware subsystem.

**Tools to exercise** (35):
- `unifi_create_wlan`
- `unifi_list_wlans`
- `unifi_get_wlan`
- `unifi_update_wlan`
- `unifi_delete_wlan`
- `unifi_create_route`
- `unifi_list_routes`
- `unifi_get_route`
- `unifi_update_route`
- `unifi_delete_route`
- `unifi_create_dns_record`
- `unifi_list_dns_records`
- `unifi_get_dns_record`
- `unifi_update_dns_record`
- `unifi_delete_dns_record`
- `unifi_create_broadcast_group`
- `unifi_list_broadcast_groups`
- `unifi_get_broadcast_group`
- `unifi_update_broadcast_group`
- `unifi_delete_broadcast_group`
- `unifi_create_media_file`
- `unifi_list_media_files`
- `unifi_get_media_file`
- `unifi_update_media_file`
- `unifi_delete_media_file`
- `unifi_create_radius_account`
- `unifi_list_radius_accounts`
- `unifi_get_radius_account`
- `unifi_update_radius_account`
- `unifi_delete_radius_account`
- `unifi_list_device_configs`
- `unifi_list_channel_plans`
- `unifi_list_virtual_devices`
- `unifi_list_known_rogue_aps`
- `unifi_list_elements`

**Steps**:
1. **Create** using `unifi_create_wlan` with `confirm=True` **[Hardware-dependent — expect error]** (Requires AP group (needs adopted APs). Expect ApGroupMissing error):
    - `name`: `bt_sys26_wlan`
    - `security`: `wpapsk`
    - `wpa_mode`: `wpa2`
    - `wpa_enc`: `ccmp`
    - `x_passphrase`: `testpassword12345678`
2. **List** using `unifi_list_wlans` — verify the created resource appears
3. **Get** using `unifi_get_wlan` with the ID from the create response
4. **Update** using `unifi_update_wlan` with `confirm=True` — set `name` to `bt_sys26_wlan_upd`
5. **Get** again using `unifi_get_wlan` — verify `name` was updated
6. **Create** using `unifi_create_route` with `confirm=True` **[Hardware-dependent — expect error]** (Requires gateway device. Expect 500 error):
    - `name`: `bt_sys26_route`
    - `type`: `static-route`
    - `static-route_network`: `10.99.99.0/24`
    - `static-route_nexthop`: `192.168.1.1`
    - `enabled`: `True`
7. **List** using `unifi_list_routes` — verify the created resource appears
8. **Get** using `unifi_get_route` with the ID from the create response
9. **Update** using `unifi_update_route` with `confirm=True` — set `name` to `bt_sys26_route_upd`
10. **Get** again using `unifi_get_route` — verify `name` was updated
11. **Create** using `unifi_create_dns_record` with `confirm=True` **[Hardware-dependent — expect error]** (May require specific device types):
    - `name`: `bt_sys26_dns`
12. **List** using `unifi_list_dns_records` — verify the created resource appears
13. **Get** using `unifi_get_dns_record` with the ID from the create response
14. **Update** using `unifi_update_dns_record` with `confirm=True` — set `name` to `bt_sys26_dns_upd`
15. **Get** again using `unifi_get_dns_record` — verify `name` was updated
16. **Create** using `unifi_create_broadcast_group` with `confirm=True` **[Hardware-dependent — expect error]**:
    - `name`: `bt_sys26_bcast`
17. **List** using `unifi_list_broadcast_groups` — verify the created resource appears
18. **Get** using `unifi_get_broadcast_group` with the ID from the create response
19. **Update** using `unifi_update_broadcast_group` with `confirm=True` — set `name` to `bt_sys26_bcast_upd`
20. **Get** again using `unifi_get_broadcast_group` — verify `name` was updated
21. **Create** using `unifi_create_media_file` with `confirm=True` **[Hardware-dependent — expect error]**:
    - `name`: `bt_sys26_media`
22. **List** using `unifi_list_media_files` — verify the created resource appears
23. **Get** using `unifi_get_media_file` with the ID from the create response
24. **Update** using `unifi_update_media_file` with `confirm=True` — set `name` to `bt_sys26_media_upd`
25. **Get** again using `unifi_get_media_file` — verify `name` was updated
26. **Create** using `unifi_create_radius_account` with `confirm=True` **[Hardware-dependent — expect error]**:
    - `name`: `bt_sys26_radaccount`
27. **List** using `unifi_list_radius_accounts` — verify the created resource appears
28. **Get** using `unifi_get_radius_account` with the ID from the create response
29. **Update** using `unifi_update_radius_account` with `confirm=True` — set `name` to `bt_sys26_radaccount_upd`
30. **Get** again using `unifi_get_radius_account` — verify `name` was updated
31. **Read** using `unifi_list_device_configs` **[Hardware-dependent — may return empty or error]** (REST read-only, may return empty without devices)
32. **Read** using `unifi_list_channel_plans` **[Hardware-dependent — may return empty or error]**
33. **Read** using `unifi_list_virtual_devices` **[Hardware-dependent — may return empty or error]**
34. **Read** using `unifi_list_known_rogue_aps` **[Hardware-dependent — may return empty or error]**
35. **Read** using `unifi_list_elements` **[Hardware-dependent — may return empty or error]**

**Important notes**:
These endpoints require adopted devices. Expect 400/404/500 errors.
The test verifies the tool exists and returns a sensible error, not that it succeeds.

**Cleanup** (reverse order):
- Delete using `unifi_delete_radius_account` with `confirm=True` (ID from create step)
- Delete using `unifi_delete_media_file` with `confirm=True` (ID from create step)
- Delete using `unifi_delete_broadcast_group` with `confirm=True` (ID from create step)
- Delete using `unifi_delete_dns_record` with `confirm=True` (ID from create step)
- Delete using `unifi_delete_route` with `confirm=True` (ID from create step)
- Delete using `unifi_delete_wlan` with `confirm=True` (ID from create step)

**Expected outcome**: All 35 tools exercised successfully.
