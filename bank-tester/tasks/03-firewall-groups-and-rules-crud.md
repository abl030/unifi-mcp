## Task 03: Firewall Groups and Rules CRUD

**task_id**: 03-firewall-groups-and-rules-crud

**Objective**: Exercise all tools in the firewall subsystem.

**Tools to exercise** (10):
- `unifi_create_firewall_group`
- `unifi_list_firewall_groups`
- `unifi_get_firewall_group`
- `unifi_update_firewall_group`
- `unifi_delete_firewall_group`
- `unifi_create_firewall_rule`
- `unifi_list_firewall_rules`
- `unifi_get_firewall_rule`
- `unifi_update_firewall_rule`
- `unifi_delete_firewall_rule`

**Steps**:
1. **Create** using `unifi_create_firewall_group` with `confirm=True`:
    - `name`: `bt_sys03_fwgroup`
    - `group_type`: `address-group`
    - `group_members`: `['192.168.99.0/24']`
2. **List** using `unifi_list_firewall_groups` — verify the created resource appears
3. **Get** using `unifi_get_firewall_group` with the ID from the create response
4. **Update** using `unifi_update_firewall_group` with `confirm=True` — set `name` to `bt_sys03_fwgroup_upd`
5. **Get** again using `unifi_get_firewall_group` — verify `name` was updated
6. **Create** using `unifi_create_firewall_rule` with `confirm=True`:
    - `name`: `bt_sys03_fwrule`
    - `action`: `drop`
    - `ruleset`: `WAN_IN`
    - `protocol`: `all`
    - `rule_index`: `4000`
    - `protocol_match_excepted`: `False`
    - `src_firewallgroup_ids`: `[]`
    - `src_mac_address`: ``
    - `src_address`: ``
    - `src_networkconf_id`: ``
    - `src_networkconf_type`: `NETv4`
    - `dst_firewallgroup_ids`: `[]`
    - `dst_address`: ``
    - `dst_networkconf_id`: ``
    - `dst_networkconf_type`: `NETv4`
    - `state_new`: `True`
    - `state_established`: `True`
    - `state_related`: `True`
    - `state_invalid`: `False`
    - `logging`: `False`
    - `ipsec`: ``
    - `enabled`: `True`
7. **List** using `unifi_list_firewall_rules` — verify the created resource appears
8. **Get** using `unifi_get_firewall_rule` with the ID from the create response
9. **Update** using `unifi_update_firewall_rule` with `confirm=True` — set `name` to `bt_sys03_fwrule_upd`
10. **Get** again using `unifi_get_firewall_rule` — verify `name` was updated

**Cleanup** (reverse order):
- Delete using `unifi_delete_firewall_rule` with `confirm=True` (ID from create step)
- Delete using `unifi_delete_firewall_group` with `confirm=True` (ID from create step)

**Expected outcome**: All 10 tools exercised successfully.
