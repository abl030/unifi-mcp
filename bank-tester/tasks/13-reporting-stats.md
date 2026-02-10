## Task 13: Reporting Stats

**task_id**: 13-reporting-stats

**Objective**: Exercise all tools in the stats subsystem.

**Tools to exercise** (10):
- `unifi_list_report`
- `unifi_list_speedtest_results`
- `unifi_list_report_5min_gateway`
- `unifi_list_report_hourly_gateway`
- `unifi_list_report_daily_gateway`
- `unifi_list_report_monthly_site`
- `unifi_list_report_monthly_ap`
- `unifi_list_report_monthly_user`
- `unifi_list_report_monthly_gateway`
- `unifi_list_report_5min_ap`

**Steps**:
1. **Read stat** using `unifi_list_report`
2. **Read stat** using `unifi_list_speedtest_results`
3. **Read stat** using `unifi_list_report_5min_gateway`
4. **Read stat** using `unifi_list_report_hourly_gateway`
5. **Read stat** using `unifi_list_report_daily_gateway`
6. **Read stat** using `unifi_list_report_monthly_site`
7. **Read stat** using `unifi_list_report_monthly_ap`
8. **Read stat** using `unifi_list_report_monthly_user`
9. **Read stat** using `unifi_list_report_monthly_gateway`
10. **Read stat** using `unifi_list_report_5min_ap`

**Cleanup** (reverse order):
- No cleanup needed (read-only / settings restored)

**Expected outcome**: All 10 tools exercised successfully.
