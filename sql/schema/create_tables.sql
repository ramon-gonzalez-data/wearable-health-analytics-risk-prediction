-- *********************************************
-- Wearable Health Analytics - Postgres Schema
-- File: sql/schema/create_tables.sql
-- *********************************************

BEGIN;

-- ---------------
-- 1) MEMBERS
-- ---------------
CREATE TABLE IF NOT EXISTS members (
   member_id		BIGSERIAL PRIMARY KEY,
   external_member_id	TEXT UNIQUE,
   first_name		TEXT NOT NULL,
   last_name		TEXT NOT NULL,
   date_of_birth	DATE NOT NULL,
   gender		TEXT CHECK (
      gender IN ('Male', 'Female', 'Non-binary', 'Other', 'Prefer not to say', 'Unknown')),
   phone		TEXT,
   email		TEXT,
   city			TEXT,
   state 		TEXT,
   zip_code		TEXT,
   country		TEXT NOT NULL DEFAULT 'United States',
   created_at		TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- --------------
-- 2) DEVICES
-- --------------
CREATE TABLE IF NOT EXISTS devices (
   device_id	   BIGSERIAL PRIMARY KEY,
   device_serial   TEXT NOT NULL UNIQUE,
   device_type	   TEXT NOT NULL,  -- glucose_monitor, heart_monitor
   manufacturer	   TEXT,
   model	   TEXT,
   sim_type	   TEXT CHECK (sim_type IN ('SIM', 'USIM', 'eSIM', 'iSIM')), -- Physical SIM or embedded
   created_at	   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ---------------------------------
-- 3) MEMBER_DEVICES (bridge table)
------------------------------------
CREATE TABLE IF NOT EXISTS member_devices (
   member_device_id   BIGSERIAL PRIMARY KEY,
   member_id   	      BIGINT NOT NULL REFERENCES members(member_id) ON DELETE CASCADE,
   device_id	      BIGINT NOT NULL REFERENCES devices(device_id) ON DELETE CASCADE,
   assigned_at	      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
   unassigned_at      TIMESTAMPTZ, 
   CONSTRAINT chk_member_devices_dates CHECK (unassigned_at IS NULL OR unassigned_at >= assigned_at)
);

-- ----------------------
-- 4) WEARABLE_READINGS
-- ----------------------
CREATE TABLE IF NOT EXISTS wearable_readings (
   reading_id	   BIGSERIAL PRIMARY KEY,
   member_id	   BIGINT NOT NULL REFERENCES members(member_id) ON DELETE CASCADE,
   device_id	   BIGINT REFERENCES devices(device_id) ON DELETE SET NULL,
   recorded_at	   TIMESTAMPTZ NOT NULL,
   heart_rate_bpm  SMALLINT CHECK (heart_rate_bpm BETWEEN 20 AND 250),
   systolic_mmHg   SMALLINT CHECK (systolic_mmHg BETWEEN 50 AND 250),
   diastolic_mmHg  SMALLINT CHECK (diastolic_mmHg BETWEEN 30 AND 150),
   glucose_mg_dl   SMALLINT CHECK (glucose_mg_dl BETWEEN 30 AND 600),
   spo2_pct	   NUMERIC(5,2) CHECK (spo2_pct BETWEEN 50 AND 100),
   created_at	   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- -------------------------
-- 5) TELEMEDICINE_VISITS
-- ------------------------
CREATE TABLE IF NOT EXISTS telemedicine_visits (
   visit_id         BIGSERIAL PRIMARY KEY,       
   member_id        BIGINT NOT NULL REFERENCES members(member_id) ON DELETE CASCADE,
   visit_start_at   TIMESTAMPTZ NOT NULL,
   visit_end_at     TIMESTAMPTZ,
   clinician_name   TEXT,
   reason	    TEXT,
   notes	    TEXT,
   created_at	    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
   CONSTRAINT chk_telemed_dates CHECK (visit_end_at IS NULL OR visit_end_at >= visit_start_at)
);

-- -----------------------
-- 6) ALERTS_GENERATED
-- ------------------------
CREATE TABLE IF NOT EXISTS alerts_generated (
   alert_id	      BIGSERIAL PRIMARY KEY,
   member_id	      BIGINT NOT NULL REFERENCES members(member_id) ON DELETE CASCADE,
   reading_id	      BIGINT REFERENCES wearable_readings(reading_id) ON DELETE SET NULL,
   alert_type	      TEXT NOT NULL,
   severity	      TEXT NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
   alert_message      TEXT,
   triggered_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
   acknowledged_at    TIMESTAMPTZ,
   CONSTRAINT chk_alert_ack_time CHECK (acknowledged_at IS NULL OR acknowledged_at >= triggered_at)
);

COMMIT;






