TRUNCATE reviews;
\COPY reviews(asin,overall,"reviewText","reviewTime","reviewerID","reviewerName",summary) FROM 'reviews.csv' DELIMITER ',' CSV HEADER;

TRUNCATE products;
\COPY products(asin,brand,description,"imgUrl",price,title) FROM 'products.csv' DELIMITER ',' CSV HEADER;


TRUNCATE product_categories;
\COPY product_categories(asin,category,"salesRank") FROM 'product_categories.csv' DELIMITER ',' CSV HEADER;

TRUNCATE review_topics;
\COPY review_topics(asin,"reviewerID",topic) FROM 'review_topics.csv' DELIMITER ',' CSV HEADER;
