"""Tool naming conventions, command mappings, and test payloads."""

from __future__ import annotations

# Resource name → (singular, plural) for tool naming
# e.g. networkconf → ("network", "networks") → unifi_list_networks, unifi_get_network
RESOURCE_NAMES: dict[str, tuple[str, str]] = {
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
}

# Stat endpoint name → display name for tools
STAT_NAMES: dict[str, str] = {
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
    # evtmgr
    ("evtmgr", "archive-all-alarms"): "archive_all_alarms",
    # sitemgr
    ("sitemgr", "add-site"): "add_site",
    ("sitemgr", "delete-site"): "delete_site",
    ("sitemgr", "update-site"): "update_site",
    ("sitemgr", "get-admins"): "get_admins",
    ("sitemgr", "move-device"): "move_device",
    ("sitemgr", "delete-device"): "delete_device",
    # backup
    ("backup", "list-backups"): "list_backups",
    ("backup", "delete-backup"): "delete_backup",
    # system
    ("system", "backup"): "create_backup",
    # stat
    ("stat", "clear-dpi"): "clear_dpi",
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
    # evtmgr
    ("evtmgr", "archive-all-alarms"): {},
    # sitemgr
    ("sitemgr", "add-site"): {"desc": "str"},
    ("sitemgr", "delete-site"): {"site": "str"},
    ("sitemgr", "update-site"): {"desc": "str"},
    ("sitemgr", "get-admins"): {},
    ("sitemgr", "move-device"): {"mac": "str", "site": "str"},
    ("sitemgr", "delete-device"): {"mac": "str"},
    # backup
    ("backup", "list-backups"): {},
    ("backup", "delete-backup"): {"filename": "str"},
    # system
    ("system", "backup"): {},
    # stat
    ("stat", "clear-dpi"): {},
}

# Commands that are safe to run in tests (no side effects on real devices)
SAFE_TEST_COMMANDS: set[tuple[str, str]] = {
    ("devmgr", "set-locate"),
    ("devmgr", "unset-locate"),
    ("devmgr", "speedtest-status"),
    ("evtmgr", "archive-all-alarms"),
    ("sitemgr", "get-admins"),
    ("backup", "list-backups"),
}

# Commands that mutate state and need confirm=True
MUTATION_COMMANDS: set[tuple[str, str]] = set(COMMAND_TOOL_NAMES.keys()) - {
    ("devmgr", "speedtest-status"),
    ("sitemgr", "get-admins"),
    ("backup", "list-backups"),
}

# v2 resource name → (singular, plural)
V2_RESOURCE_NAMES: dict[str, tuple[str, str]] = {
    "firewall_policies": ("firewall_policy", "firewall_policies"),
    "traffic_rules": ("traffic_rule", "traffic_rules"),
}

# Stat endpoints that need method/body overrides for tests
# session requires POST with params — GET returns 400 InvalidArgs
STAT_OVERRIDES: dict[str, dict] = {
    "session": {"method": "POST", "body": {"mac": "00:00:00:00:00:00"}},
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
HARDWARE_DEPENDENT_REST: set[str] = {"routing", "wlanconf"}

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

# REST resources that are read-only (no create/update/delete)
READ_ONLY_REST: set[str] = {"setting", "alarm", "event"}

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
