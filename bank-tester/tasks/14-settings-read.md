## Task 14: Settings Read

**task_id**: 14-settings-read

**Objective**: Exercise all tools in the settings subsystem.

**Tools to exercise** (2):
- `unifi_list_settings`
- `unifi_get_setting`

**Steps**:
1. **Read** using `unifi_list_settings`
2. **Read setting** using `unifi_get_setting` with `key="super_identity"`
3. **Read setting** using `unifi_get_setting` with `key="snmp"`
4. **Read setting** using `unifi_get_setting` with `key="mgmt"`
5. **Read setting** using `unifi_get_setting` with `key="country"`
6. **Read setting** using `unifi_get_setting` with `key="locale"`
7. **Read setting** using `unifi_get_setting` with `key="guest_access"`
8. **Read setting** using `unifi_get_setting` with `key="ntp"`
9. **Read setting** using `unifi_get_setting` with `key="connectivity"`
10. **Read setting** using `unifi_get_setting` with `key="auto_speedtest"`
11. **Read setting** using `unifi_get_setting` with `key="baresip"`
12. **Read setting** using `unifi_get_setting` with `key="broadcast"`
13. **Read setting** using `unifi_get_setting` with `key="doh"`
14. **Read setting** using `unifi_get_setting` with `key="dpi"`
15. **Read setting** using `unifi_get_setting` with `key="element_adopt"`
16. **Read setting** using `unifi_get_setting` with `key="ether_lighting"`
17. **Read setting** using `unifi_get_setting` with `key="global_ap"`
18. **Read setting** using `unifi_get_setting` with `key="global_switch"`
19. **Read setting** using `unifi_get_setting` with `key="ips"`
20. **Read setting** using `unifi_get_setting` with `key="lcm"`
21. **Read setting** using `unifi_get_setting` with `key="magic_site_to_site_vpn"`
22. **Read setting** using `unifi_get_setting` with `key="network_optimization"`
23. **Read setting** using `unifi_get_setting` with `key="porta"`
24. **Read setting** using `unifi_get_setting` with `key="radio_ai"`
25. **Read setting** using `unifi_get_setting` with `key="radius"`
26. **Read setting** using `unifi_get_setting` with `key="rsyslogd"`
27. **Read setting** using `unifi_get_setting` with `key="super_cloudaccess"`
28. **Read setting** using `unifi_get_setting` with `key="super_events"`
29. **Read setting** using `unifi_get_setting` with `key="super_fwupdate"`
30. **Read setting** using `unifi_get_setting` with `key="super_mail"`
31. **Read setting** using `unifi_get_setting` with `key="super_mgmt"`
32. **Read setting** using `unifi_get_setting` with `key="super_sdn"`
33. **Read setting** using `unifi_get_setting` with `key="super_smtp"`
34. **Read setting** using `unifi_get_setting` with `key="teleport"`
35. **Read setting** using `unifi_get_setting` with `key="usg"`
36. **Read setting** using `unifi_get_setting` with `key="usw"`

**Important notes**:
All 35 setting categories read via unifi_get_setting with key parameter.
Also test unifi_list_settings to list all categories.

**Cleanup** (reverse order):
- No cleanup needed (read-only / settings restored)

**Expected outcome**: All 2 tools exercised successfully.
