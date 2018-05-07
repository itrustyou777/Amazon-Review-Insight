from __future__ import print_function

import sys
import os
import itertools

from pyspark.context import SparkContext
from pyspark.sql import SparkSession, SQLContext, Row
from pyspark.sql.functions import to_timestamp, regexp_replace
from pyspark.sql.types import *

password = os.environ['RDS_PASSWORD']

mode = "append"
url = "jdbc:postgresql://insight.c0lqcrqaigco.us-east-1.rds.amazonaws.com:5432/amazon_review_insight"
properties = {"user": "mijik", "password": password, "driver": "org.postgresql.Driver"}
null = u'\u0000'

sc = SparkContext.getOrCreate()
sqlContext = SQLContext(sc)


#products_df = sqlContext.read.option("mode", "DROPMALFORMED").option('charset', 'UTF-8').json("s3a://amazon-review-insight/products_small.json")
products_df = sqlContext.read.option("mode", "DROPMALFORMED").option('charset', 'UTF-8').json("s3a://amazon-review-insight/metadata.json")
products_df = products_df.toDF("asin", "brand", "categories", "description", "imgUrl",
                               "price", "related", "salesRank", "title")

clean_products_df = products_df.where(products_df.asin.isNotNull()).drop("categories", "related", "salesRank")

# toPandas() : bring back data to master node, and save it as csv file with Pandas data frame. found it on stackoverflow
# write the data to S3 to avoid storing everything in the Master memory
clean_products_df.write.jdbc(url=url, table="products", mode=mode, properties=properties)

#reviews_df = sqlContext.read.option("mode", "DROPMALFORMED").option('charset', 'UTF-8').json("s3a://amazon-review-insight/reviews_small.json")
reviews_df = sqlContext.read.option("mode", "DROPMALFORMED").option('charset', 'UTF-8').json("s3a://amazon-review-insight/item_dedup.json")
reviews_df = reviews_df.toDF("asin", "helpful", "overall", "reviewText", "reviewTimeStr",
                             "reviewerID", "reviewerName", "summary", "unixReviewTime")

# to_timestamp parses the date so that it's correctly loaded in postgres
reviews_df = reviews_df.withColumn("reviewTime", to_timestamp(reviews_df['reviewTimeStr'], 'MM dd,yyyy'))

reviews_df = reviews_df.withColumn('reviewText', regexp_replace(reviews_df['reviewText'], null, ''))
reviews_df = reviews_df.withColumn('summary', regexp_replace(reviews_df['summary'], null, ''))
reviews_df = reviews_df.withColumn('reviewerName', regexp_replace(reviews_df['reviewerName'], null, ''))

clean_reviews_df = reviews_df.where(reviews_df.asin.isNotNull() &
                                    reviews_df.reviewerID.isNotNull()).drop("helpful", "unixReviewTime", "reviewTimeStr")

# toPandas() : bring back data to master node, and save it as csv file with Pandas data frame. found it on stackoverflow
# write the data to S3 to avoid storing everything in the Master memory
clean_reviews_df.write.jdbc(url=url, table='reviews', mode=mode, properties=properties)


def toCategories(row):
# instead of [], set() to prevent duplicated values.
    result = set()
    if row.salesRank:
        salesRank = row.salesRank.asDict()
    else:
        salesRank = {}
    for category in itertools.chain.from_iterable(row.categories or []):
        rank = salesRank.get(category)
        if rank:
            rank = int(rank)
# to not process "row.asin(None)" nor len(row.asin) == 0, Same for category 
        if row.asin and len(row.asin) > 0 and category and len(category) > 0:
            result.add(Row(row.asin, category, rank))
    return list(result)
# not possible to see the "result", those are on slave node

# First toDF() is to creat DataFrame, Second toDF() is to name colums
# flatMap is ID c1,c2,c3 -> ID c1, Id c2, Id c3.
# products_df.rdd.flatMap(toCategories) is Row(_1=u'0001048791', _2=u'Books', _3=6334800)
product_categories_df = products_df.rdd.flatMap(toCategories).toDF().toDF("asin", "category", "salesRank")


# to delete duplicated values
clean_product_categories_df = product_categories_df.where(product_categories_df.asin.isNotNull() &
                                                        product_categories_df.category.isNotNull()).dropDuplicates()

clean_product_categories_df.write.jdbc(url=url, table='product_categories', mode=mode, properties=properties)

#simple pattern mathing.
reviews_topics_rules = {
  "price": ["price"],
  "delivery": ["delivery"],
  "appearance": ["looks"],
  "function": ["works well", "doesn't work", "not working"],
  "service": ["good service"]
}


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

reviews_topics_df = clean_reviews_df.rdd.flatMap(toTopic).toDF().toDF('asin', 'reviewerID', 'topic')
clean_reviews_topics_df = reviews_topics_df.where(reviews_topics_df.asin.isNotNull() & 
                                                  reviews_topics_df.reviewerID.isNotNull() & 
                                                  reviews_topics_df.topic.isNotNull()).dropDuplicates()
clean_reviews_topics_df.write.jdbc(url=url, table='review_topics', mode=mode, properties=properties)
