FROM apache/airflow:2.9.3-python3.11

USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends openjdk-17-jdk-headless \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

USER airflow
RUN pip install --no-cache-dir \
    pyspark==3.5.1 pandas==2.2.2 pyarrow==16.1.0 \
    psycopg2-binary==2.9.9 dbt-core==1.8.2 dbt-postgres==1.8.2
