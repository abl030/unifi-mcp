"""Tool naming conventions, command mappings, and test payloads."""

from __future__ import annotations

# Resource name → (singular, plural) for tool naming
# e.g. networkconf → ("network", "networks") → unifi_list_networks, unifi_get_network
RESOURCE_NAMES: dict[str, tuple[str, str]] = {
    # --- Core (existing) ---
    "networkconf": ("network", "networks"),
    "wlanconf": ("wlan", "wlans"),
    "wlangroup": ("wlan_group", "wlan_groups"),
    "portconf": ("port_profile", "port_profiles"),
    "portforward": ("port_forward", "port_forwards"),
    "firewallrule": ("firewall_rule", "firewall_rules"),
    "firewallgroup": ("firewall_group", "firewall_groups"),
    "dynamicdns": ("dynamic_dns", "dynamic_dns_entries"),
    "routing": ("route", "routes"),
    "usergroup": ("user_group", "user_groups"),
    "user": ("user", "users"),
    "tag": ("tag", "tags"),
    "setting": ("setting", "settings"),
    "alarm": ("alarm", "alarms"),
    "event": ("event", "events"),
    "radiusprofile": ("radius_profile", "radius_profiles"),
    "account": ("account", "accounts"),
    # --- Discovered by probe (CRUD) ---
    "hotspotop": ("hotspot_operator", "hotspot_operators"),
    "hotspotpackage": ("hotspot_package", "hotspot_packages"),
    "hotspot2conf": ("hotspot2_config", "hotspot2_configs"),
    "radiusaccount": ("radius_account", "radius_accounts"),
    "broadcastgroup": ("broadcast_group", "broadcast_groups"),
    "mediafile": ("media_file", "media_files"),
    "scheduletask": ("schedule_task", "schedule_tasks"),
    "map": ("map", "maps"),
    "dnsrecord": ("dns_record", "dns_records"),
    "dhcpoption": ("dhcp_option", "dhcp_options"),
    "heatmap": ("heatmap", "heatmaps"),
    "heatmappoint": ("heatmap_point", "heatmap_points"),
    "spatialrecord": ("spatial_record", "spatial_records"),
    "dpiapp": ("dpi_app", "dpi_apps"),
    "dpigroup": ("dpi_group", "dpi_groups"),
    # --- Discovered by probe (read-only) ---
    "device": ("device_config", "device_configs"),
    "channelplan": ("channel_plan", "channel_plans"),
    "virtualdevice": ("virtual_device", "virtual_devices"),
    "rogueknown": ("known_rogue_ap", "known_rogue_aps"),
    "element": ("element", "elements"),
}

# Stat endpoint name → display name for tools
STAT_NAMES: dict[str, str] = {
    # --- Core (existing) ---
    "device": "devices",
    "sta": "clients",
    "health": "health",
    "event": "stat_events",
    "alarm": "stat_alarms",
    "rogueap": "rogue_aps",
    "sitedpi": "site_dpi",
    "stadpi": "client_dpi",
    "dynamicdns": "dynamic_dns_stats",
    "portforward": "port_forward_stats",
    "sysinfo": "sysinfo",
    "ccode": "country_codes",
    "current_channel": "current_channels",
    "device_basic": "devices_basic",
    "routing": "routing_stats",
    "authorization": "authorizations",
    "session": "sessions",
    "report": "report",
    # --- Discovered by probe ---
    "guest": "guests",
    "dashboard": "dashboard",
    "spectrum_scan": "spectrum_scans",
    "alluser": "all_users",
    "voucher": "vouchers",
    "payment": "payments",
    "sdn": "sdn_status",
    "gateway": "gateway_stats",
    "dpi": "dpi_stats",
    "remoteuservpn": "remote_user_vpn",
    "anomalies": "anomalies",
    "ips_event": "ips_events",
    "report_archive_speedtest": "speedtest_results",
    "report_5min_gw": "report_5min_gateway",
    "report_hourly_gw": "report_hourly_gateway",
    "report_daily_gw": "report_daily_gateway",
    "report_monthly_site": "report_monthly_site",
    "report_monthly_ap": "report_monthly_ap",
    "report_monthly_user": "report_monthly_user",
    "report_monthly_gw": "report_monthly_gateway",
    "report_5min_ap": "report_5min_ap",
}

# (manager, command) → tool function name (without unifi_ prefix)
COMMAND_TOOL_NAMES: dict[tuple[str, str], str] = {
    # stamgr
    ("stamgr", "block-sta"): "block_client",
    ("stamgr", "unblock-sta"): "unblock_client",
    ("stamgr", "kick-sta"): "kick_client",
    ("stamgr", "forget-sta"): "forget_client",
    ("stamgr", "unauthorize-guest"): "unauthorize_guest",
    ("stamgr", "authorize-guest"): "authorize_guest",
    ("stamgr", "reconnect-sta"): "reconnect_client",
    # devmgr
    ("devmgr", "adopt"): "adopt_device",
    ("devmgr", "restart"): "restart_device",
    ("devmgr", "force-provision"): "force_provision_device",
    ("devmgr", "power-cycle"): "power_cycle_port",
    ("devmgr", "speedtest"): "run_speedtest",
    ("devmgr", "speedtest-status"): "get_speedtest_status",
    ("devmgr", "set-locate"): "locate_device",
    ("devmgr", "unset-locate"): "unlocate_device",
    ("devmgr", "upgrade"): "upgrade_device",
    ("devmgr", "upgrade-external"): "upgrade_device_external",
    ("devmgr", "migrate"): "migrate_device",
    ("devmgr", "cancel-migrate"): "cancel_migrate_device",
    ("devmgr", "spectrum-scan"): "spectrum_scan",
    ("devmgr", "rename"): "rename_device",
    ("devmgr", "led-override"): "led_override_device",
    ("devmgr", "disable-ap"): "disable_ap",
    ("devmgr", "rolling-upgrade"): "rolling_upgrade",
    ("devmgr", "cancel-rolling-upgrade"): "cancel_rolling_upgrade",
    ("devmgr", "check-firmware-update"): "check_firmware_update",
    ("devmgr", "upgrade-all-devices"): "upgrade_all_devices",
    ("devmgr", "advanced-adopt"): "advanced_adopt_device",
    ("devmgr", "set-rollupgrade"): "set_rollupgrade",
    ("devmgr", "unset-rollupgrade"): "unset_rollupgrade",
    ("devmgr", "restart-http-portal"): "restart_http_portal",
    ("devmgr", "enable"): "enable_device",
    ("devmgr", "disable"): "disable_device",
    ("devmgr", "cable-test"): "cable_test",
    ("devmgr", "set-inform"): "set_inform_device",
    # evtmgr
    ("evtmgr", "archive-all-alarms"): "archive_all_alarms",
    ("evtmgr", "archive-alarm"): "archive_alarm",
    # sitemgr
    ("sitemgr", "add-site"): "add_site",
    ("sitemgr", "delete-site"): "delete_site",
    ("sitemgr", "update-site"): "update_site",
    ("sitemgr", "get-admins"): "get_admins",
    ("sitemgr", "move-device"): "move_device",
    ("sitemgr", "delete-device"): "delete_device",
    ("sitemgr", "site-leds"): "set_site_leds",
    ("sitemgr", "invite-admin"): "invite_admin",
    ("sitemgr", "assign-existing-admin"): "assign_existing_admin",
    ("sitemgr", "update-admin"): "update_admin",
    ("sitemgr", "revoke-admin"): "revoke_admin",
    ("sitemgr", "delete-admin"): "delete_admin",
    ("sitemgr", "grant-super-admin"): "grant_super_admin",
    ("sitemgr", "create-admin"): "create_admin",
    ("sitemgr", "revoke-super-admin"): "revoke_super_admin",
    ("sitemgr", "set-site-name"): "set_site_name",
    # backup
    ("backup", "list-backups"): "list_backups",
    ("backup", "delete-backup"): "delete_backup",
    ("backup", "generate-backup"): "generate_backup",
    ("backup", "generate-backup-site"): "generate_backup_site",
    # system
    ("system", "backup"): "create_backup",
    ("system", "reboot-cloudkey"): "reboot_cloudkey",
    ("system", "element-adoption"): "element_adoption",
    ("system", "download-backup"): "download_backup",
    # stat
    ("stat", "reset-dpi"): "clear_dpi",
    # hotspot
    ("hotspot", "authorize-guest"): "hotspot_authorize_guest",
    ("hotspot", "create-voucher"): "create_voucher",
    ("hotspot", "revoke-voucher"): "revoke_voucher",
    ("hotspot", "extend-guest-validity"): "extend_guest_validity",
    ("hotspot", "delete-voucher"): "delete_voucher",
    # alarm
    ("alarm", "archive"): "alarm_archive",
}

# Extra parameters required by each command (beyond "cmd")
# mac = client MAC, _id/mac for device commands
COMMAND_PARAMS: dict[tuple[str, str], dict[str, str]] = {
    # stamgr - all require mac
    ("stamgr", "block-sta"): {"mac": "str"},
    ("stamgr", "unblock-sta"): {"mac": "str"},
    ("stamgr", "kick-sta"): {"mac": "str"},
    ("stamgr", "forget-sta"): {"macs": "list"},
    ("stamgr", "unauthorize-guest"): {"mac": "str"},
    ("stamgr", "authorize-guest"): {"mac": "str", "minutes": "int"},
    ("stamgr", "reconnect-sta"): {"mac": "str"},
    # devmgr
    ("devmgr", "adopt"): {"mac": "str"},
    ("devmgr", "restart"): {"mac": "str"},
    ("devmgr", "force-provision"): {"mac": "str"},
    ("devmgr", "power-cycle"): {"mac": "str", "port_idx": "int"},
    ("devmgr", "speedtest"): {},
    ("devmgr", "speedtest-status"): {},
    ("devmgr", "set-locate"): {"mac": "str"},
    ("devmgr", "unset-locate"): {"mac": "str"},
    ("devmgr", "upgrade"): {"mac": "str"},
    ("devmgr", "upgrade-external"): {"mac": "str", "url": "str"},
    ("devmgr", "migrate"): {"mac": "str", "inform_url": "str"},
    ("devmgr", "cancel-migrate"): {"mac": "str"},
    ("devmgr", "spectrum-scan"): {"mac": "str"},
    ("devmgr", "rename"): {"mac": "str", "name": "str"},
    ("devmgr", "led-override"): {"mac": "str", "led_override": "str"},
    ("devmgr", "disable-ap"): {"mac": "str"},
    ("devmgr", "rolling-upgrade"): {},
    ("devmgr", "cancel-rolling-upgrade"): {},
    ("devmgr", "check-firmware-update"): {},
    ("devmgr", "upgrade-all-devices"): {},
    ("devmgr", "advanced-adopt"): {"mac": "str", "url": "str", "key": "str"},
    ("devmgr", "set-rollupgrade"): {"mac": "str"},
    ("devmgr", "unset-rollupgrade"): {"mac": "str"},
    ("devmgr", "restart-http-portal"): {},
    ("devmgr", "enable"): {"mac": "str"},
    ("devmgr", "disable"): {"mac": "str"},
    ("devmgr", "cable-test"): {"mac": "str", "port_idx": "int"},
    ("devmgr", "set-inform"): {"mac": "str", "inform_url": "str"},
    # evtmgr
    ("evtmgr", "archive-all-alarms"): {},
    ("evtmgr", "archive-alarm"): {"_id": "str"},
    # sitemgr
    ("sitemgr", "add-site"): {"desc": "str"},
    ("sitemgr", "delete-site"): {"site": "str"},
    ("sitemgr", "update-site"): {"desc": "str"},
    ("sitemgr", "get-admins"): {},
    ("sitemgr", "move-device"): {"mac": "str", "site": "str"},
    ("sitemgr", "delete-device"): {"mac": "str"},
    ("sitemgr", "site-leds"): {"led_enabled": "bool"},
    ("sitemgr", "invite-admin"): {"email": "str", "name": "str", "role": "str"},
    ("sitemgr", "assign-existing-admin"): {"admin": "str", "role": "str"},
    ("sitemgr", "update-admin"): {"admin": "str", "role": "str"},
    ("sitemgr", "revoke-admin"): {"admin": "str"},
    ("sitemgr", "delete-admin"): {"admin": "str"},
    ("sitemgr", "grant-super-admin"): {"admin": "str"},
    ("sitemgr", "create-admin"): {"name": "str", "email": "str", "x_password": "str", "role": "str"},
    ("sitemgr", "revoke-super-admin"): {"admin": "str"},
    ("sitemgr", "set-site-name"): {"desc": "str"},
    # backup
    ("backup", "list-backups"): {},
    ("backup", "delete-backup"): {"filename": "str"},
    ("backup", "generate-backup"): {},
    ("backup", "generate-backup-site"): {},
    # system
    ("system", "backup"): {},
    ("system", "reboot-cloudkey"): {},
    ("system", "element-adoption"): {"mac": "str"},
    ("system", "download-backup"): {"filename": "str"},
    # stat
    ("stat", "reset-dpi"): {},
    # hotspot
    ("hotspot", "authorize-guest"): {"mac": "str", "minutes": "int"},
    ("hotspot", "create-voucher"): {"expire": "int", "n": "int", "quota": "int"},
    ("hotspot", "revoke-voucher"): {"_id": "str"},
    ("hotspot", "extend-guest-validity"): {"_id": "str"},
    ("hotspot", "delete-voucher"): {"_id": "str"},
    # alarm
    ("alarm", "archive"): {"_id": "str"},
}

# Commands that are safe to run in tests (no side effects on real devices)
SAFE_TEST_COMMANDS: set[tuple[str, str]] = {
    ("devmgr", "set-locate"),
    ("devmgr", "unset-locate"),
    ("devmgr", "speedtest-status"),
    ("devmgr", "check-firmware-update"),
    ("evtmgr", "archive-all-alarms"),
    ("sitemgr", "get-admins"),
    ("backup", "list-backups"),
}

# Commands that mutate state and need confirm=True
MUTATION_COMMANDS: set[tuple[str, str]] = set(COMMAND_TOOL_NAMES.keys()) - {
    ("devmgr", "speedtest-status"),
    ("devmgr", "check-firmware-update"),
    ("sitemgr", "get-admins"),
    ("backup", "list-backups"),
}

# v2 resource name → (singular, plural)
V2_RESOURCE_NAMES: dict[str, tuple[str, str]] = {
    "firewall_policies": ("firewall_policy", "firewall_policies"),
    "traffic_rules": ("traffic_rule", "traffic_rules"),
    "clients_active": ("active_client", "active_clients"),
    "clients_history": ("client_history", "clients_history"),
    "apgroups": ("ap_group", "ap_groups"),
    "trafficroutes": ("traffic_route", "traffic_routes"),
    "firewall_zones": ("firewall_zone", "firewall_zones"),
}

# Stat endpoints that need method/body overrides for tests
# session requires POST with params — GET returns 400 InvalidArgs
STAT_OVERRIDES: dict[str, dict] = {
    "session": {"method": "POST", "body": {"type": "all", "start": 0, "end": 9999999999}},
}

# Commands that are safe but need a real device (return error without one)
# These are still tested — we assert the correct error response to prove the endpoint works
DEVICE_DEPENDENT_COMMANDS: set[tuple[str, str]] = {
    ("devmgr", "set-locate"),
    ("devmgr", "unset-locate"),
}

# REST resources that need hardware to create successfully
# routing: needs gateway device, returns 500 without one
# wlanconf: needs AP group (requires adopted APs), returns 400 ApGroupMissing
# device/dnsrecord/broadcastgroup/element: needs adopted devices
HARDWARE_DEPENDENT_REST: set[str] = {
    "routing", "wlanconf", "device", "dnsrecord", "broadcastgroup", "element",
    "mediafile", "radiusaccount",
}

# Global endpoints that should be skipped in integration tests
UNTESTABLE_GLOBALS: set[str] = {
    "logout",           # Breaks the test session
    "system_poweroff",  # Would power off the controller
    "system_reboot",    # Would reboot the controller
}

# Minimal payloads to create REST resources in tests
MINIMAL_CREATE_PAYLOADS: dict[str, dict] = {
    "networkconf": {
        "name": "test_network_{unique}",
        "purpose": "vlan-only",
        "vlan_enabled": True,
        "vlan": 999,
    },
    "wlanconf": {
        "name": "test_wlan_{unique}",
        "security": "wpapsk",
        "wpa_mode": "wpa2",
        "wpa_enc": "ccmp",
        "x_passphrase": "testpassword12345678",
        "networkconf_id": "{default_network_id}",
    },
    "wlangroup": {
        "name": "test_wlangroup_{unique}",
    },
    "portconf": {
        "name": "test_portprofile_{unique}",
        "forward": "customize",
        "native_networkconf_id": "{default_network_id}",
    },
    "portforward": {
        "name": "test_portforward_{unique}",
        "fwd": "192.168.1.100",
        "fwd_port": "8080",
        "dst_port": "9090",
        "proto": "tcp_udp",
    },
    "firewallrule": {
        "name": "test_fwrule_{unique}",
        "action": "drop",
        "ruleset": "WAN_IN",
        "protocol": "all",
        "rule_index": 4000,
        "protocol_match_excepted": False,
        "src_firewallgroup_ids": [],
        "src_mac_address": "",
        "src_address": "",
        "src_networkconf_id": "",
        "src_networkconf_type": "NETv4",
        "dst_firewallgroup_ids": [],
        "dst_address": "",
        "dst_networkconf_id": "",
        "dst_networkconf_type": "NETv4",
        "state_new": True,
        "state_established": True,
        "state_related": True,
        "state_invalid": False,
        "logging": False,
        "ipsec": "",
        "enabled": True,
    },
    "firewallgroup": {
        "name": "test_fwgroup_{unique}",
        "group_type": "address-group",
        "group_members": ["192.168.1.0/24"],
    },
    "dynamicdns": {
        "service": "dyndns",
        "host_name": "test_{unique}.example.com",
        "login": "testuser",
        "x_password": "testpass",
    },
    "routing": {
        "name": "test_route_{unique}",
        "type": "static-route",
        "static-route_network": "10.99.99.0/24",
        "static-route_nexthop": "192.168.1.1",
        "enabled": True,
    },
    "usergroup": {
        "name": "test_usergroup_{unique}",
    },
    "tag": {
        "name": "test_tag_{unique}",
        "member_table": [],
    },
    "radiusprofile": {
        "name": "test_radius_{unique}",
        "auth_servers": [{"ip": "192.168.1.200", "port": 1812, "x_secret": "secret"}],
    },
    "account": {
        "name": "test_account_{unique}",
        "x_password": "testpassword",
    },
}

# REST resources where PUT requires the full object, not just changed fields.
# The update tool docstrings will warn about this.
FULL_OBJECT_UPDATE_REST: set[str] = {
    "scheduletask",
}

# REST resources that don't support DELETE via the REST API.
# The delete tool is skipped for these resources.
NO_REST_DELETE: set[str] = {
    "user",  # Users are removed via forget-sta (unifi_forget_client), not REST DELETE
}

# v2 resource create hints: extra docstring info for resources without samples
V2_CREATE_HINTS: dict[str, str] = {
    "traffic_rules": (
        "Required: action (str: 'BLOCK'|'ALLOW'), enabled (bool), "
        "matching_target (str: 'INTERNET'|'LOCAL_NETWORK'), "
        "target_devices (list of {type: 'ALL_CLIENTS'|'CLIENT'|'NETWORK', client_mac/network_id}), "
        "network_id (str, _id from unifi_list_networks)"
    ),
    "firewall_policies": (
        "Required: action (str), ipVersion (str: 'V4'|'V6'), "
        "source (obj with zoneId from unifi_list_firewall_zones), "
        "destination (obj with zoneId from unifi_list_firewall_zones), "
        "schedule (obj with mode, e.g. {'mode': 'ALWAYS'}). "
        "Note: Requires firewall zones which are created when a gateway device is adopted."
    ),
    "trafficroutes": (
        "Required: targetDevices (list, non-empty device refs), "
        "networkId (str, _id from unifi_list_networks), "
        "matchingTarget (str: 'INTERNET'|'LOCAL_NETWORK')"
    ),
}

# Required field hints for resources with empty api-samples.
# Used in create tool docstrings when schema inference has no data.
REQUIRED_CREATE_FIELDS: dict[str, str] = {
    "hotspotpackage": (
        "Required: name (str), amount (int, price in cents, 0=free), "
        "currency (str, e.g. 'USD'), hours (int, access duration in hours), "
        "bytes (int, bandwidth limit, 0=unlimited). "
        "Note: Requires hotspot portal + payment gateway configured on the controller."
    ),
    "dhcpoption": (
        "Required: name (str), code (int, DHCP option number 7-254 excluding "
        "reserved: 15,42,43,44,51,66,67,252), value (str). "
        "Note: May require a DHCP-enabled network with gateway device."
    ),
    "heatmap": (
        "Required: name (str), map_id (str, _id from unifi_list_maps)"
    ),
    "heatmappoint": (
        "Required: heatmap_id (str, _id from unifi_list_heatmaps), "
        "x (float, 0.0–1.0), y (float, 0.0–1.0)"
    ),
    "spatialrecord": (
        "Required: name (str), devices (list, device references e.g. []), "
        "description (str, e.g. 'Room label')"
    ),
}

# REST resources that are read-only (no create/update/delete)
READ_ONLY_REST: set[str] = {
    "setting", "alarm", "event",
    "device", "channelplan", "virtualdevice", "rogueknown", "element",
}

# REST resources that support CRUD (create, update, delete)
CRUD_REST: set[str] = set(RESOURCE_NAMES.keys()) - READ_ONLY_REST

# Resources where settings has special handling (keyed by 'key' field)
SETTINGS_RESOURCE = "setting"

# Cross-reference hints: field name → tool to call to find valid IDs
# Used in docstrings to help AI consumers chain tool calls correctly
ID_CROSS_REFS: dict[str, str] = {
    "native_networkconf_id": "unifi_list_networks",
    "networkconf_id": "unifi_list_networks",
    "voice_networkconf_id": "unifi_list_networks",
    "last_connection_network_id": "unifi_list_networks",
    "portconf_id": "unifi_list_port_profiles",
    "wlangroup_id": "unifi_list_wlan_groups",
    "usergroup_id": "unifi_list_user_groups",
    "radiusprofile_id": "unifi_list_radius_profiles",
    "src_firewallgroup_ids": "unifi_list_firewall_groups",
    "dst_firewallgroup_ids": "unifi_list_firewall_groups",
    "src_networkconf_id": "unifi_list_networks",
    "dst_networkconf_id": "unifi_list_networks",
    "ap_group_ids": "unifi_list_wlan_groups",
}

# Workflow hints: resource name → note appended to create/update docstrings
# Helps AI consumers know what to do next after creating a resource
WORKFLOW_HINTS: dict[str, str] = {
    "networkconf": "Tip: Use this network's _id as native_networkconf_id in port profiles or networkconf_id in WLANs.",
    "firewallgroup": "Tip: Reference this group's _id in src_firewallgroup_ids or dst_firewallgroup_ids when creating firewall rules.",
    "portconf": "Tip: Apply this profile to switch ports via unifi_set_port_override with portconf_id.",
    "firewallrule": "Tip: Create firewall groups first (unifi_create_firewall_group) to use in src/dst_firewallgroup_ids.",
    "portforward": "Tip: Ensure the destination IP (fwd) is a static address or DHCP reservation on your network.",
    "wlanconf": "Tip: Requires a network (networkconf_id from unifi_list_networks) and at least one adopted AP.",
    "radiusprofile": "Tip: Reference this profile's _id as radiusprofile_id when configuring WLANs with 802.1X authentication.",
    "usergroup": "Tip: Assign users to this group by setting usergroup_id when creating or updating users.",
    "user": "Note: To remove a user, use unifi_forget_client with the user's MAC address. REST DELETE is not supported for the user resource.",
}
