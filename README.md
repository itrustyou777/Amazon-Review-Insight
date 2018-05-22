# Amazon-Review-Insight

## Introduction
These days feedback from customers' reviews is crucial to online businesses. In this project, I'm analyzing a dataset of 142.8 million Amazon product reviews which are collected over 18 years.

I developed an interactive dashboard that displays Amazon product reviews classified by topics. Specifically, the topics are price, delivery, function, appearance, and service. The dashboard also allows you to add new topics or edit existing topics. Furthermore, there is a fast search for products and reviews.

## Demo
[http://www.mijious.us](http://www.mijious.us "Amazon review insight")

## Archtecture
![alt text](https://github.com/itrustyou777/Amazon-Review-Insight/blob/master/data-pipeline.png "DataPipeLine")

* S3 -- storage for Amazon review and product data.
* Spark -- cleaning data, pre-aggregating, pre-calculating, classifying reviews by topics, loading data to PostgreSQL.
* PostgreSQL -- database, querying
* Flask -- dashboard 

## Challenges

* Building data pipeline
* Batch processing of reviews data -- transformation, loading, tuning the Spark cluster and the PostgreSQL database.  
* Query optimization -- the main queries used in the dashboard, especially product and reviews search, and displaying charts
* Handling incremental updates of topics when new topic rules are added or modified

## Prerequisites & installation
[TBD]


## Author
[Miji Kim](https://www.linkedin.com/in/mijik/ "Miji's Linkedin")

