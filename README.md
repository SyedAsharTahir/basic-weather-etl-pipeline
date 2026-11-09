# Weather ETL Pipeline

A small ETL pipeline that pulls hourly weather data from the [Open-Meteo](https://open-meteo.com/) API for four Pakistani cities, validates it, and loads it into a Dockerized PostgreSQL database.

**Cities:** Karachi, Lahore, Islamabad, Peshawar

## How it works

```
Open-Meteo API -> extract -> transform + validate -> upsert into Postgres
```

- **Extract:** fetches hourly temperature, humidity, wind speed, precipitation and weather code per city.
- **Transform:** cleans the data with pandas and runs a bad-rows check before loading.
- **Load:** upserts into `hourly_weather` using `ON CONFLICT (city, observed_at) DO UPDATE`, so the pipeline is idempotent. Re-running it never creates duplicates, and revised values overwrite old ones.

## Stack

Python, pandas, PostgreSQL 16, Docker Compose, psycopg2

## Setup

```bash
# 1. Start Postgres
docker compose up -d

# 2. Create a virtual environment and install dependencies
python3 -m venv venv
source venv/bin/activate
pip install pandas requests psycopg2-binary

# 3. Create the table (first run only)
docker compose exec db psql -U pipeline -d weather -c "
CREATE TABLE IF NOT EXISTS hourly_weather (
    city                 TEXT      NOT NULL,
    observed_at          TIMESTAMP NOT NULL,
    temperature_2m       REAL,
    relative_humidity_2m INTEGER,
    wind_speed_10m       REAL,
    precipitation        REAL,
    weather_code         INTEGER,
    PRIMARY KEY (city, observed_at)
);"
```

## Usage

```bash
# Load the latest data
python pipeline.py daily

# Load a historical range
python pipeline.py backfill 2024-09-11 2026-10-11
```

## Check the data

```bash
docker compose exec db psql -U pipeline -d weather \
  -c "SELECT city, count(*), min(observed_at), max(observed_at) FROM hourly_weather GROUP BY city;"
```

## Roadmap

- [ ] Schedule the daily run with Apache Airflow
- [ ] Add dbt models (daily aggregates per city) with data tests
- [ ] Move credentials to environment variables
