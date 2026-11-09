select
    city,
    observed_at::date as day,
    round(Avg(temperature_2m)::numeric,1) as avg_temp,
    max(temperature_2m) as max_temp,
    min(temperature_2m) as min_temp,
    sum(precipitation) as total_rain
    from {{source('raw','hourly_weather')}}
    group by city,observed_at::date
