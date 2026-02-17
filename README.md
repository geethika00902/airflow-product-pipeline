Airflow-Based Price Analytics Pipeline
📖 Project Description

This project is an end-to-end automated data engineering pipeline that collects product price data, processes and cleans it using Python, orchestrates workflows using Apache Airflow, stores data in PostgreSQL, and visualizes trends using Power BI. The entire system is containerized with Docker.

🏗 System Architecture
Web Scraping (Python)
        ↓
Data Cleaning
        ↓
Apache Airflow (Orchestration)
        ↓
PostgreSQL (Storage)
        ↓
Power BI (Dashboards)

🛠 Technologies Used

Python

Apache Airflow

Docker & Docker Compose

PostgreSQL

Git & GitHub

Power BI

📂 Project Structure
airflow_project/
│
├── dags/
│   ├── product_price_pipeline.py
│   ├── scripts/
│       ├── cleaning/
│       └── loaders/
│
├── data/
├── logs/
├── docker-compose.yaml
└── README.md

⚙️ Key Features

Automated daily Airflow pipelines

Data cleaning and transformation using Python

Historical price tracking

PostgreSQL-based data storage

Dockerized environment

Power BI dashboards for analytics

▶ How to Run the Project
1. Start Docker Containers
docker compose up -d

2. Open Airflow UI
http://172.30.8.141:8080

3. Run Pipeline

Enable and trigger the product_price_pipeline DAG.

📊 Database Tables

mobiles

laptops

refrigerators

televisions

price_history


What I Learned

Building data pipelines with Apache Airflow

Containerization using Docker

Working with PostgreSQL databases

Automating workflows

Data visualization with Power BI
