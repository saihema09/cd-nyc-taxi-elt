from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator

PROJ = "/opt/airflow/project"

with DAG(
    dag_id="nyc_taxi_elt",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    max_active_runs=1,
    catchup=False,
    params={"month": "2024-01"},
) as dag:

    bronze = BashOperator(task_id="bronze",
        bash_command=f"cd {PROJ} && python src/bronze.py {{{{ params.month }}}}")
    silver = BashOperator(task_id="silver",
        bash_command=f"cd {PROJ} && python src/silver.py {{{{ params.month }}}}")
    load = BashOperator(task_id="load",
        bash_command=f"cd {PROJ} && python src/load.py {{{{ params.month }}}}")
    dbt_build = BashOperator(task_id="dbt_build",
        bash_command=f"cd {PROJ}/dbt_project/taxi_dbt && dbt build --profiles-dir .")
    recon = BashOperator(task_id="reconcile",
        bash_command=f"cd {PROJ} && python quality/reconcile.py {{{{ params.month }}}}")

    bronze >> silver >> load >> dbt_build >> recon
