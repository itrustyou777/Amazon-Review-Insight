-- Tables

CREATE TABLE public.product_categories (
    asin character(15) NOT NULL,
    category character varying NOT NULL
);

CREATE TABLE public.products (
    asin character(15) NOT NULL,
    brand character varying,
    description text,
    "imgUrl" character varying,
    price numeric(12,2),
    title character varying,
    reviewCount integer,
    avgOverall decimal(10, 2)
);

CREATE TABLE public.review_topics (
    asin character(15) NOT NULL,
    "reviewerID" character(50) NOT NULL,
    topic character varying NOT NULL
);

CREATE TABLE public.reviews (
    id serial,
    "reviewerName" character varying,
    overall real,
    "reviewText" text,
    summary text,
    "reviewTime" date,
    asin character(15) NOT NULL,
    "reviewerID" character(50) NOT NULL
);
