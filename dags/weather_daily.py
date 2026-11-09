from datetime import datetime
from airflow.sdk import DAG # type: ignore
from airflow.providers.standard.operators.bash import BashOperator # type: ignore
with DAG(
    dag_id="weather_daily",
    start_date=datetime(2026,11,1),
    schedule="@daily",
    catchup=False
)as dag:
    run_pipeline=BashOperator(task_id="run_pipeline",
                              bash_command="cd ~/projects/etl-pipeline  && " \
                              "~/venvs/etl/bin/python pipeline.py daily  ")