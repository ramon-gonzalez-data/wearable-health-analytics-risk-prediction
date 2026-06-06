/*
File: create_member_ml_dataset_views.sql

Purpose:
Create a machine learning dataset.

Workflow:
1. member_health_features
   - Aggregate wearable readings into one row per member.
   - Calculate health metrics (AVG, MAX, MIN).

2. member_risk_points
   - Convert health metrics into risk points.
   - Score are glucose, blood pressure, oxygen saturation,
     heart rate, and age.

3. member_ml_dataset
   - Calculate risk_score.
   - Assign risk_level (Low, Medium, High).
   - Final dataset used for Random Forest training.

Output:
One row per member with:
- Engineered health features
- Risk score
- Risk level
*/


/*
===============================================================================
VIEW 1
member_health_features

Purpose:
Aggregate wearable readings into a member-level health profile.
===============================================================================
*/

CREATE OR REPLACE VIEW member_health_features AS

SELECT
    m.member_id,
    m.date_of_birth,

    ROUND(AVG(w.heart_rate_bpm), 2) AS avg_heart_rate,
    MAX(w.heart_rate_bpm) AS max_heart_rate,

    ROUND(AVG(w.systolic_mmHg), 2) AS avg_systolic_bp,
    MAX(w.systolic_mmHg) AS max_systolic_bp,

    ROUND(AVG(w.diastolic_mmHg), 2) AS avg_diastolic_bp,
    MAX(w.diastolic_mmHg) AS max_diastolic_bp,

    ROUND(AVG(w.glucose_mg_dl), 2) AS avg_glucose,
    MAX(w.glucose_mg_dl) AS max_glucose,

    ROUND(AVG(w.spo2_pct), 2) AS avg_spo2,
    MIN(w.spo2_pct) AS min_spo2

FROM members m
JOIN wearable_readings w
    ON m.member_id = w.member_id

GROUP BY
    m.member_id,
    m.date_of_birth;


/*
===============================================================================
VIEW 2
member_risk_points

Purpose:
Convert health metrics into risk points.
===============================================================================
*/

CREATE OR REPLACE VIEW member_risk_points AS

SELECT
    member_id,

    EXTRACT(
        YEAR FROM AGE(
            CURRENT_DATE,
            date_of_birth
        )
    ) AS age,

    avg_heart_rate,
    max_heart_rate,

    avg_systolic_bp,
    max_systolic_bp,

    avg_diastolic_bp,
    max_diastolic_bp,

    avg_glucose,
    max_glucose,

    avg_spo2,
    min_spo2,

    /* Glucose Risk Points */
    CASE
        WHEN max_glucose >= 180 THEN 2
        WHEN max_glucose >= 140 THEN 1
        ELSE 0
    END AS glucose_points,

    /* Blood Pressure Risk Points */
    CASE
        WHEN max_systolic_bp >= 160
          OR max_diastolic_bp >= 100 THEN 2
        WHEN max_systolic_bp >= 140
          OR max_diastolic_bp >= 90 THEN 1
        ELSE 0
    END AS blood_pressure_points,

    /* Oxygen Saturation Risk Points */
    CASE
        WHEN min_spo2 < 92 THEN 2
        WHEN min_spo2 < 95 THEN 1
        ELSE 0
    END AS spo2_points,

    /* Heart Rate Risk Points */
    CASE
        WHEN max_heart_rate >= 140 THEN 2
        WHEN max_heart_rate >= 120 THEN 1
        ELSE 0
    END AS heart_rate_points,

    /* Age Risk Points */
    CASE
        WHEN EXTRACT(
                YEAR FROM AGE(
                    CURRENT_DATE,
                    date_of_birth
                )
             ) >= 65 THEN 2

        WHEN EXTRACT(
                YEAR FROM AGE(
                    CURRENT_DATE,
                    date_of_birth
                )
             ) >= 50 THEN 1

        ELSE 0
    END AS age_points

FROM member_health_features;


/*
===============================================================================
VIEW 3
member_ml_dataset

Purpose:
Create the final machine learning dataset.

Risk Score:
Sum of all risk points.

Risk Levels:
0 - 2  = Low
3 - 5  = Medium
6 +    = High

This final view will create the dataset, then will be exported to CSV and used
for Random Forest training.
===============================================================================
*/

CREATE OR REPLACE VIEW member_ml_dataset AS

SELECT
    member_id,
    age,

    avg_heart_rate,
    max_heart_rate,

    avg_systolic_bp,
    max_systolic_bp,

    avg_diastolic_bp,
    max_diastolic_bp,

    avg_glucose,
    max_glucose,

    avg_spo2,
    min_spo2,

    glucose_points,
    blood_pressure_points,
    spo2_points,
    heart_rate_points,
    age_points,

    (
        glucose_points
        + blood_pressure_points
        + spo2_points
        + heart_rate_points
        + age_points
    ) AS risk_score,

    CASE
        WHEN (
            glucose_points
            + blood_pressure_points
            + spo2_points
            + heart_rate_points
            + age_points
        ) >= 6
        THEN 'High'

        WHEN (
            glucose_points
            + blood_pressure_points
            + spo2_points
            + heart_rate_points
            + age_points
        ) >= 3
        THEN 'Medium'

        ELSE 'Low'
    END AS risk_level

FROM member_risk_points;
