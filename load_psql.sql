-- reviews_df = reviews_df.toDF("reviewAsin", "helpful", "overall", "reviewText", "reviewTime",
--                              "reviewerID", "reviewerName", "summary", "unixReviewTime")

TRUNCATE reviews;
\COPY reviews(asin,overall,"reviewText","reviewTime","reviewerID","reviewerName",summary) FROM 'reviews.csv' DELIMITER ',' CSV HEADER;

-- products_df = products_df.toDF("asin", "brand", "categories", "description", "imUrl",
--                               "price", "related", "salesRank", "title")

TRUNCATE products;
\COPY products(asin,brand,description,"imgUrl",price,title) FROM 'products.csv' DELIMITER ',' CSV HEADER;


TRUNCATE product_categories;
\COPY product_categories(asin,category,"salesRank") FROM 'product_categories.csv' DELIMITER ',' CSV HEADER;

TRUNCATE review_topics;
\COPY review_topics(asin,"reviewerID",topic) FROM 'review_topics.csv' DELIMITER ',' CSV HEADER;
