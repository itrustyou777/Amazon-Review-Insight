-- Tables

CREATE UNLOGGED TABLE IF NOT EXISTS public.review_topics_tmp (
    asin character(15) NOT NULL,
    "reviewerID" character(50) NOT NULL,
    topic character varying NOT NULL
);

