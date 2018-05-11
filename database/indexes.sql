-- Indexes 

 CREATE INDEX reviews_sentiment_time_index ON reviews (asin, sentiment, (cast(extract(year from "reviewTime") as text) || '-' || cast(extract(month from
"reviewTime") as text)));

CLUSTER reviews USING reviews_sentiment_time_index;


CREATE INDEX products_title_index ON products USING GIN (to_tsvector('english', title));
CREATE INDEX reviews_summary_and_text_index ON reviews USING GIN (to_tsvector('english', summary || ' ' || "reviewText"));

CREATE INDEX reviews_overall_desc_index ON reviews (overall DESC);
CREATE INDEX reviews_overall_asc_index ON reviews (overall ASC);

