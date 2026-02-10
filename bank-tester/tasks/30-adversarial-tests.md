## Task 30: Adversarial Tests

**task_id**: 30-adversarial

**Objective**: Test error handling by intentionally sending bad inputs across multiple endpoints.

**Instructions**: For each test case below, make the API call exactly as specified. Record the error response quality: does it clearly explain what went wrong? Does it suggest the correct values?

**Steps**:
1. **Missing required 'name' field**: Call `unifi_create_network` with `purpose='vlan-only'`, `confirm=True`
   - Expected: Error about missing name field
   - Rate error message quality: clear/unclear/missing
2. **Invalid enum value for 'purpose'**: Call `unifi_create_network` with `name='bt_adv_bad_purpose'`, `purpose='invalid_purpose_value'`, `confirm=True`
   - Expected: Error about invalid purpose value
   - Rate error message quality: clear/unclear/missing
3. **Non-existent resource ID**: Call `unifi_update_network` with `id='000000000000000000000000'`, `data={'name': 'bt_adv_nonexistent'}`, `confirm=True`
   - Expected: Error about resource not found
   - Rate error message quality: clear/unclear/missing
4. **Non-existent resource ID**: Call `unifi_delete_network` with `id='000000000000000000000000'`, `confirm=True`
   - Expected: Error about resource not found
   - Rate error message quality: clear/unclear/missing
5. **Non-existent setting key**: Call `unifi_get_setting` with `key='nonexistent_setting_key_xyz'`
   - Expected: Error or empty result about setting not found
   - Rate error message quality: clear/unclear/missing
6. **Invalid data type for setting**: Call `unifi_update_setting` with `key='snmp'`, `data='not_a_dict'`, `confirm=True`
   - Expected: Error about invalid data type
   - Rate error message quality: clear/unclear/missing
7. **Invalid MAC address format**: Call `unifi_block_client` with `mac='not-a-mac'`, `confirm=True`
   - Expected: Error about invalid MAC format
   - Rate error message quality: clear/unclear/missing
8. **Missing required fields for firewall rule**: Call `unifi_create_firewall_rule` with `name='bt_adv_incomplete_rule'`, `confirm=True`
   - Expected: Error about missing required fields
   - Rate error message quality: clear/unclear/missing
9. **Invalid port number**: Call `unifi_create_port_forward` with `name='bt_adv_bad_port'`, `fwd='192.168.1.100'`, `fwd_port='99999'`, `dst_port='-1'`, `proto='tcp_udp'`, `confirm=True`
   - Expected: Error about invalid port number
   - Rate error message quality: clear/unclear/missing
10. **Valid no-param call (should always succeed)**: Call `unifi_status` with 
   - Expected: Success — controller status
   - Rate error message quality: clear/unclear/missing

**Tools to exercise** (9):
- `unifi_create_network`
- `unifi_update_network`
- `unifi_delete_network`
- `unifi_get_setting`
- `unifi_update_setting`
- `unifi_block_client`
- `unifi_create_firewall_rule`
- `unifi_create_port_forward`
- `unifi_status`

**Expected outcome**: All calls should fail with clear error messages (except the status call). No resources should be created.

**Cleanup**: None needed (all calls should fail).
