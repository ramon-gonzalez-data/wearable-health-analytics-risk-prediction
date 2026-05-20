-- Create dim_member table
CREATE TABLE dim_member AS
SELECT
    member_id AS member_key,
    external_member_id,
    first_name,
    last_name,
    date_of_birth,
    sex_at_birth,
    city,
    state,
    zip_code,
    country
FROM members;

-- Create dim_device table
CREATE TABLE dim_device AS
SELECT
    device_id AS device_key,
    device_serial,
    device_type,
    manufacturer,
    model,
    sim_type
FROM devices;

-- Create dim_date table
CREATE TABLE dim_date AS
SELECT DISTINCT
    TO_CHAR(recorded_at, 'YYYYMMDD')::INT AS date_key,
    DATE(recorded_at) AS full_date,
    EXTRACT(YEAR FROM recorded_at)::INT AS year,
    EXTRACT(MONTH FROM recorded_at)::INT AS month,
    EXTRACT(DAY FROM recorded_at)::INT AS day,
    TO_CHAR(recorded_at, 'Month') AS month_name,
    TO_CHAR(recorded_at, 'Mon') AS month_short,
    EXTRACT(DOW FROM recorded_at)::INT AS day_of_week,
    TO_CHAR(recorded_at, 'Day') AS day_name,
    CASE 
        WHEN EXTRACT(DOW FROM recorded_at) IN (0,6) THEN 'Weekend'
        ELSE 'Weekday'
    END AS day_type
FROM wearable_readings
ORDER BY date_key;

-- Create dim_time table
CREATE TABLE dim_time AS
SELECT DISTINCT
    TO_CHAR(recorded_at, 'HH24MI')::INT AS time_key,
    EXTRACT(HOUR FROM recorded_at)::INT AS hour,
    EXTRACT(MINUTE FROM recorded_at)::INT AS minute
FROM wearable_readings
ORDER BY time_key;

-- Create fact_wearable_readings
CREATE TABLE fact_wearable_readings AS
SELECT
    reading_id,
    member_id AS member_key,
    device_id AS device_key,
    TO_CHAR(recorded_at, 'YYYYMMDD')::INT AS date_key,
    TO_CHAR(recorded_at, 'HH24MI')::INT AS time_key,
    heart_rate_bpm,
    systolic_mmHg,
    diastolic_mmHg,
    glucose_mg_dl,
    spo2_pct
FROM wearable_readings;




