\copy member_devices (member_id, device_id, assigned_at, unassigned_at) FROM '/home/master/gitprojects/wearable-health-analytics/data/raw/member_devices_raw.csv' WITH (FORMAT csv, HEADER true, NULL '');

