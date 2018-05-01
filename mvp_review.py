from __future__ import print_function

import sys
import itertools

from pyspark.context import SparkContext
from pyspark.sql import SparkSession, SQLContext, Row
from pyspark.sql.functions import udf
from pyspark.sql.types import *


sc = SparkContext.getOrCreate()
sqlContext = SQLContext(sc)

# READ products Json files into a DataFrame
products_df = sqlContext.read.json("s3a://amazon-review-insight/products_small.json")
products_df = products_df.toDF("asin", "brand", "categories", "description", "imUrl",
                               "price", "related", "salesRank", "title")

# Clean data which doesn't have Asin
clean_products_df = products_df.where(products_df.asin.isNotNull()).drop("categories", "related", "salesRank")

# toPandas() : bring back data to master node, and save it as csv file with Pandas data frame. found it on stackoverflow
clean_products_df.toPandas().to_csv('products.csv', index=False)

# READ review Json files into a DataFrame
reviews_df = sqlContext.read.json("s3a://amazon-review-insight/reviews_small.json")
reviews_df = reviews_df.toDF("reviewAsin", "helpful", "overall", "reviewText", "reviewTime",
                             "reviewerID", "reviewerName", "summary", "unixReviewTime")

# clean out data which doesn't have Asin or reviewerID.
clean_reviews_df = reviews_df.where(reviews_df.reviewAsin.isNotNull() &
                                    reviews_df.reviewerID.isNotNull()).drop("helpful", "unixReviewTime")

# toPandas() : bring back data to master node, and save it as csv file with Pandas data frame. found it on stackoverflow
clean_reviews_df.toPandas().to_csv('reviews.csv', index=False)


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
#to not process "row.asin(None)" nor len(row.asin) == 0, Same for category 
        if row.asin and len(row.asin) > 0 and category and len(category) > 0:
            result.add(Row(row.asin, category, rank))
    return list(result)
# not possible to see the "result", those are on slave node

# First toDF() is to creat DataFrame
# Second toDF() is to name colums
# flatMap is ID c1,c2,c3 -> ID c1, Id c2, Id c3.
# products_df.rdd.flatMap(toCategories) is Row(_1=u'0001048791', _2=u'Books', _3=6334800)
product_categories_df = products_df.rdd.flatMap(toCategories).toDF().toDF("asin", "category", "salesRank")


# to delete duplicated values
clean_product_categories_df = product_categories_df.where(product_categories_df.asin.isNotNull() &
                                                        product_categories_df.category.isNotNull()).dropDuplicates()

clean_product_categories_df.toPandas().to_csv('product_categories.csv', index=False)

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
        result.append(Row(row.reviewAsin, row.reviewerID, topic))

    return result

reviews_topics_df = clean_reviews_df.rdd.flatMap(toTopic).toDF().toDF('reviewAsin', 'reviewerID', 'topic')
clean_reviews_topics_df = reviews_topics_df.dropDuplicates()
clean_reviews_topics_df.toPandas().to_csv('review_topics.csv', index=False)

