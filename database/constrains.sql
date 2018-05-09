ALTER TABLE ONLY public.product_categories
    ADD CONSTRAINT product_categories_pkey PRIMARY KEY (asin, category);


ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (asin);


ALTER TABLE ONLY public.review_topics
    ADD CONSTRAINT review_topics_pkey PRIMARY KEY (asin, "reviewerID", topic);


ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_pkey PRIMARY KEY ("reviewerID", asin);
