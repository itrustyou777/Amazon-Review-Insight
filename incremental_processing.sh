#!/bin/bash

master_hostname=$(hostname)

./database/run_sql.sh database/schema_tmp.sql
./database/run_sql.sh <(echo "TRUNCATE ONLY review_topics_tmp")

$SPARK_HOME/bin/spark-submit --conf "spark.executor.memory=3g" --conf "spark.hadoop.fs.s3a.block.size=67108864" --master spark://${master_hostname}.ec2.internal:7077 --jars postgresql-42.2.2.jar incremental_process_and_load.py

./database/run_sql.sh <(echo "DROP TABLE review_topics; ALTER TABLE review_topics_tmp RENAME TO review_topics;")
