# Wearable Health Analytics

End-to-end wearable health data analytics project simulating wearable device data
used by health insurance and health tech companies.

# Project goals
- Simulate wearable health device data
- Store and analyze patient vitals
- Detect anomalies and risk conditions
- Generate automated health alerts
- Visualize insights in Tableau

# Tech Stack
- Python (pandas, numpy)
- PostgreSQL
- SQL
- Tableau
- Pandas
- Time-series analytics


# Project Structure
See repository folders for raw data, processed data, SQL schemas, and analytics queries.

# Database Schema

The following Entity Relationship Diagram (ERD) represents the logical data model for the Wearable Health Analytics project.

The schema is designed using crow's-foot notation and includes:

- one-to-many relationship
- a many-to-many relationship resolved via a bridge table
- full historical tracking of device assignments

![ER Diagram](docs/er_diagram.png)
