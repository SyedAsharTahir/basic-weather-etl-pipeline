import requests
import numpy as np
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
url="https://api.open-meteo.com/v1/forecast"#base url the rest in it was paramters
cities=[
    {"city":"karachi","latitude":24.8608,"longitude":67.0104},
    {"city":"islamabad","latitude":33.7215,"longitude":73.0433},
    {"city":"lahore","latitude":31.558,"longitude":74.3507},
    {"city":"peshawar","latitude":34.008,"longitude":71.5785},
]
def extract():
    results=[]
    for city in cities:
        parameters={
        "latitude":city["latitude"],
        "longitude":city["longitude"],
        "hourly":"temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation,weather_code",
        "timezone":"auto",
        "past_days":1,
        "forecast_days":1,
        }
        response=requests.get(url,params=parameters,timeout=10)
        response.raise_for_status()
        data=response.json()#converts to a python dict
        results.append({"city":city["city"],"data":data})
    return results

def transform(results):
    frames=[]
    for r in results:
        df=pd.DataFrame(r["data"]["hourly"])#creates table of 48 rows
        df["city"]=r["city"]
        frames.append(df)
    weather=pd.concat(frames,ignore_index=True)#stack 4 tabels into one
    weather=weather.rename(columns={"time":"observed_at"})
    weather["observed_at"]=pd.to_datetime(weather["observed_at"])
    weather["city"]=weather["city"].str.title()
    return weather

def validation(weather):
    index=weather[(weather["relative_humidity_2m"]< 0) | (weather["relative_humidity_2m"] >100)]
    print(f"{len(index)} failed bad rows check")
    return weather.drop(index.index)

def load(weather):
    cols=["city","observed_at","temperature_2m","relative_humidity_2m","wind_speed_10m"
          ,"precipitation","weather_code"]
    sql="""
            INSERT INTO hourly_weather (city,observed_at,temperature_2m,relative_humidity_2m,
            wind_speed_10m,precipitation,weather_code)
            VALUES %s
            ON CONFLICT (city,observed_at) DO UPDATE SET
                temperature_2m=EXCLUDED.temperature_2m,
                relative_humidity_2m=EXCLUDED.relative_humidity_2m,
                wind_speed_10m=EXCLUDED.wind_speed_10m,
                precipitation=EXCLUDED.precipitation,
                weather_code=EXCLUDED.weather_code
    """
    rows=list(weather[cols].itertuples(index=False,name=None))
    conn=psycopg2.connect(host="localhost",port=5432,dbname="weather",user="pipeline",password="pipeline")
    with conn:
        with conn.cursor() as cur:
            execute_values(cur,sql,rows)
    conn.close()
    print(f"loaded {len(rows)} rows")
pastUrl="https://archive-api.open-meteo.com/v1/archive"
def fetch_history(start_date,end_date):
        results=[]
        for city in cities:
            parameters={
            "latitude":city["latitude"],
            "longitude":city["longitude"],
            "hourly":"temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation,weather_code",
            "timezone":"auto",
            "start_date":start_date,
            "end_date":end_date
            }
            response=requests.get(pastUrl,params=parameters,timeout=30)
            response.raise_for_status()
            data=response.json()#converts to a python dict
            results.append({"city":city["city"],"data":data})
        return results
if __name__=="__main__":
    results=fetch_history("2026-11-01","2026-11-06")
    weather=validation(transform(results))
    print(weather.head())
    load(weather)