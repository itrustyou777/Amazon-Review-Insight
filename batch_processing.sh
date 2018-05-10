#!/bin/sh

master_hostname=$(hostname)

./database/run_sql.sh database/truncate.sql

$SPARK_HOME/bin/spark-submit --conf "spark.executor.memory=3g" --master spark://${master_hostname}.ec2.internal:7077 --jars postgresql-42.2.2.jar batch_process_and_load.py
