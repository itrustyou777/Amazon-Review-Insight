-- Indexes 

CREATE INDEX products_title_index ON products USING GIN (to_tsvector('english', title));
CREATE INDEX reviews_summary_and_text_index ON reviews USING GIN (to_tsvector('english', summary || ' ' || "reviewText"));
CREATE INDEX product_overall_desc_index ON reviews (overall DESC);
CREATE INDEX product_overall_asc_index ON reviews (overall ASC);
