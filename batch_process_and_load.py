from __future__ import print_function

import sys
import os
import itertools
import random

from pyspark.context import SparkContext
from pyspark.sql import SparkSession, SQLContext, Row
from pyspark.sql.functions import to_timestamp, regexp_replace, udf, explode
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


# Reviews processing and loading

#reviews_df = sqlContext.read.option("mode", "DROPMALFORMED").option('charset', 'UTF-8').json("s3a://amazon-review-insight/reviews_small.json")
reviews_df = sqlContext.read.option("mode", "DROPMALFORMED").option('charset', 'UTF-8').json("s3a://amazon-review-insight/item_dedup*.json")
reviews_df = reviews_df.toDF("asin", "helpful", "overall", "reviewText", "reviewTimeStr",
                             "reviewerID", "reviewerName", "summary", "unixReviewTime")

# to_timestamp parses the date so that it's correctly loaded in postgres
reviews_df = reviews_df.withColumn("reviewTime", to_timestamp(reviews_df['reviewTimeStr'], 'MM dd,yyyy'))

null = u'\u0000'
reviews_df = reviews_df.withColumn('reviewText', regexp_replace(reviews_df['reviewText'], null, ''))
reviews_df = reviews_df.withColumn('summary', regexp_replace(reviews_df['summary'], null, ''))
reviews_df = reviews_df.withColumn('reviewerName', regexp_replace(reviews_df['reviewerName'], null, ''))

sentiment = udf(lambda overall: 0 if overall <= 3 else 1, IntegerType())
reviews_df = reviews_df.withColumn('sentiment', sentiment(reviews_df.overall))

clean_reviews_df = reviews_df.where(reviews_df.asin.isNotNull() &
                                    reviews_df.reviewerID.isNotNull()).drop("helpful", "unixReviewTime", "reviewTimeStr")

# toPandas() : bring back data to master node, and save it as csv file with Pandas data frame. found it on stackoverflow
# write the data to S3 to avoid storing everything in the Master memory
clean_reviews_df.write.jdbc(url=url, table='reviews', mode=mode, properties=properties)

agg_reviews_df = clean_reviews_df.groupBy('asin').agg({'overall': 'sum', '*': 'count'}).toDF('aggAsin', 'sumOverall', 'reviewCount') 


# Product processing and loading

#products_df = sqlContext.read.option("mode", "DROPMALFORMED").option('charset', 'UTF-8').json("s3a://amazon-review-insight/products_small.json")
products_df = sqlContext.read.option("mode", "DROPMALFORMED").option('charset', 'UTF-8').json("s3a://amazon-review-insight/metadata*.json")
products_df = products_df.toDF("asin", "brand", "categories", "description", "imgUrl",
                               "price", "related", "salesRank", "title")
clean_products_df = products_df.where(products_df.asin.isNotNull()).join(agg_reviews_df, products_df.asin == agg_reviews_df.aggAsin).orderBy('reviewCount', ascending=False)

clean_products_df.drop("categories", "related", "salesRank", "aggAsin").write.jdbc(url=url, table="products", mode=mode, properties=properties)

# Product categories processing and loading

def process_categories(categories):
# instead of [], set() to prevent duplicated values.
    result = set()

    for category in (categories or []):
	if len(category) > 0:
    	    result.add(category[0])

    return list(result)
# not possible to see the "result", those are on slave node

to_categories = udf(process_categories, ArrayType(StringType()))

product_categories_df = clean_products_df.withColumn('category',
        explode(to_categories(clean_products_df.categories))).select('asin', 'category')

clean_product_categories_df = product_categories_df.where(product_categories_df.asin.isNotNull() &
                                                          product_categories_df.category.isNotNull())

clean_product_categories_df.write.jdbc(url=url, table='product_categories', mode=mode, properties=properties)
