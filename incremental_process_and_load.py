from __future__ import print_function

import sys
import os
import itertools
import boto3
import json

from pyspark.context import SparkContext
from pyspark.sql import SparkSession, SQLContext, Row
from pyspark.sql.functions import to_timestamp, regexp_replace
from pyspark.sql.types import *

# Spark objects
sc = SparkContext.getOrCreate()
sqlContext = SQLContext(sc)

# Database Connection
rds_host = os.environ['RDS_HOST']
rds_port = os.environ['RDS_PORT']
rds_db = os.environ['RDS_DB']
rds_user = os.environ['RDS_USER']
rds_password = os.environ['RDS_PASSWORD']

mode = "append"
url = "jdbc:postgresql://{host}:{port}/{db}".format(host=rds_host, port=rds_port, db=rds_db)
properties = {"user": rds_user, "password": rds_password, "driver": "org.postgresql.Driver"}

# Get the topic rules from S3
s3 = boto3.resource('s3')
bucket = s3.Bucket('amazon-review-insight')
bucket.download_file('topic_rules.json', 'topic_rules.json')
reviews_topics_rules = json.load(open('topic_rules.json')) 

# Get the reviews
reviews_df = sqlContext.read.option("mode", "DROPMALFORMED").option('charset', 'UTF-8').json("s3a://amazon-review-insight/item_dedup.json")
reviews_df = reviews_df.toDF("asin", "helpful", "overall", "reviewText", "reviewTimeStr",
                             "reviewerID", "reviewerName", "summary", "unixReviewTime")
"""
# Reading from PostgresSQL is slow, better to go to S3 directly.
reviews_df = sqlContext.read.jdbc(url=url, 
				  table='reviews',
				  column="id",
				  lowerBound=0,
			          upperBound=100000000,
				  numPartitions=400, 
				  properties=properties)
"""

# row = review
def toTopic(row):
    topics = set()

# if any keywords are matching on reviewText, add to topics
    for topic, rules in reviews_topics_rules.items():
        for rule in rules:
            if rule in row.reviewText:
                topics.add(topic)

    result = []

    for topic in topics:
        result.append(Row(row.asin, row.reviewerID, topic))

    return result

reviews_topics_df = reviews_df.rdd.flatMap(toTopic).toDF().toDF('asin', 'reviewerID', 'topic')
clean_reviews_topics_df = reviews_topics_df.where(reviews_topics_df.asin.isNotNull() & 
                                                  reviews_topics_df.reviewerID.isNotNull() & 
                                                  reviews_topics_df.topic.isNotNull()).dropDuplicates()
clean_reviews_topics_df.write.jdbc(url=url, table='review_topics_tmp', mode=mode, properties=properties)
