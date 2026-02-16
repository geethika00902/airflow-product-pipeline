from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="product_price_pipeline",
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
) as dag:

    # CLEAN TASKS
    clean_mobiles = BashOperator(
        task_id="clean_mobiles",
        bash_command="python /opt/airflow/dags/scripts/cleaning/clean_mobiles.py"
    )

    clean_laptops = BashOperator(
        task_id="clean_laptops",
        bash_command="python /opt/airflow/dags/scripts/cleaning/clean_laptops.py"
    )

    clean_refrigerators = BashOperator(
        task_id="clean_refrigerators",
        bash_command="python /opt/airflow/dags/scripts/cleaning/clean_refrigerators.py"
    )

    clean_tvs = BashOperator(
        task_id="clean_tvs",
        bash_command="python /opt/airflow/dags/scripts/cleaning/clean_tvs.py"
    )

    # LOAD TASKS
    load_mobiles = BashOperator(
        task_id="load_mobiles",
        bash_command="python /opt/airflow/dags/scripts/loaders/load_mobiles.py"
    )

    load_laptops = BashOperator(
        task_id="load_laptops",
        bash_command="python /opt/airflow/dags/scripts/loaders/load_laptops.py"
    )

    load_refrigerators = BashOperator(
        task_id="load_refrigerators",
        bash_command="python /opt/airflow/dags/scripts/loaders/load_refrigerators.py"
    )

    load_tvs = BashOperator(
        task_id="load_tvs",
        bash_command="python /opt/airflow/dags/scripts/loaders/load_tvs.py"
    )

    load_products_main = BashOperator(
        task_id="load_products_main",
        bash_command="python /opt/airflow/dags/scripts/loaders/load_products_main.py"
    )

    load_price_history = BashOperator(
        task_id="load_price_history",
        bash_command="python /opt/airflow/dags/scripts/loaders/load_price_history.py"
    )

    # PIPELINE FLOW
    clean_mobiles >> load_mobiles
    clean_laptops >> load_laptops
    clean_refrigerators >> load_refrigerators
    clean_tvs >> load_tvs

    [load_mobiles, load_laptops, load_refrigerators, load_tvs] \
        >> load_products_main >> load_price_history
