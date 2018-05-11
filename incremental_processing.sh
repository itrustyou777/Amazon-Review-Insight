#!/bin/bash

master_hostname=$(hostname)

./database/run_sql.sh database/schema_tmp.sql
./database/run_sql.sh <(echo "TRUNCATE ONLY review_topics_tmp")

$SPARK_HOME/bin/spark-submit --conf "spark.executor.memory=2g" --master spark://${master_hostname}.ec2.internal:7077 --jars postgresql-42.2.2.jar incremental_process_and_load.py

./database/run_sql.sh <(echo "ALTER TABLE ONLY review_topics_tmp ADD CONSTRAINT review_topics_tmp_pkey PRIMARY KEY (asin, \"reviewerID\", topic)");

./database/run_sql.sh <(echo "DROP TABLE review_topics; ALTER TABLE review_topics_tmp RENAME TO review_topics; ALTER TABLE review_topics RENAME CONSTRAINT review_topics_tmp_pkey TO review_topics_pkey;")
