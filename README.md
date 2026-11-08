its basic weather etl pipeline to extract data from open-meteo and cosntruct a pipeline 
Weather data by Open-Meteo.com, CC BY 4.0
RUN:
  docker compose up -d
  python pipeline.py
