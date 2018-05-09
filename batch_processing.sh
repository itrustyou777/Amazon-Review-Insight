#!/bin/sh

master_hostname=$(hostname)

$SPARK_HOME/bin/spark-submit --conf "spark.executor.memory=3g" --conf "spark.hadoop.fs.s3a.block.size=67108864" --master spark://${master_hostname}.ec2.internal:7077 --jars postgresql-42.2.2.jar batch_process_and_load.py
