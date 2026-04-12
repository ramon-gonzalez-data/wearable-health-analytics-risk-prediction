\copy devices (device_serial, device_type, manufacturer, model, sim_type) FROM '/home/master/gitprojects/wearable-health-analytics/data/raw/devices_raw.csv' WITH (FORMAT csv, HEADER true, NULL '');
