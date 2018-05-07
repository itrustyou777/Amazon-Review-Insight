-- Tables

CREATE TABLE public.product_categories (
    asin character(15) NOT NULL,
    "salesRank" numeric(10,1),
    category character varying NOT NULL
);

CREATE TABLE public.products (
    asin character(15) NOT NULL,
    brand character varying,
    description text,
    "imgUrl" character varying,
    price numeric(12,2),
    title character varying
);

CREATE TABLE public.review_topics (
    asin character(15) NOT NULL,
    "reviewerID" character(50) NOT NULL,
    topic character varying NOT NULL
);


CREATE TABLE public.reviews (
    "reviewerName" character varying,
    overall real,
    "reviewText" text,
    summary text,
    "reviewTime" date,
    asin character(15) NOT NULL,
    "reviewerID" character(50) NOT NULL
);

-- Constrains

ALTER TABLE ONLY public.product_categories
    ADD CONSTRAINT product_categories_pkey PRIMARY KEY (asin, category);


ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (asin);


ALTER TABLE ONLY public.review_topics
    ADD CONSTRAINT review_topics_pkey PRIMARY KEY (asin, "reviewerID", topic);


ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_pkey PRIMARY KEY ("reviewerID", asin);

