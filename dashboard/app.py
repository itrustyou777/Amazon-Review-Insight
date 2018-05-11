from flask import Flask, render_template, request, g
import db
import boto3
import json
import re

app = Flask(__name__)

@app.route('/')
def index():
    q = request.args.get("q", '')

    products = []

    if q:
	query = ' & '.join(re.split('\s+', q.strip()))
        conn = db.get_conn() 
        products = db.fetchall(conn, """
			select *
                        from products p 
                        where to_tsvector('english', title) @@ to_tsquery('english', '{query}')
                        limit 15 
                       """.format(query=query))

    return render_template('index.html', q=q, products=products)

@app.route('/topics', methods=['GET', 'POST'])
def topics():
    message = ''
    s3 = boto3.resource('s3')
    bucket = s3.Bucket('amazon-review-insight')
    if request.method == 'GET':
        bucket.download_file('topic_rules.json', 'topic_rules.json')
        json_obj = json.load(open('topic_rules.json')) 
    else:
        json_obj = json.loads(request.form['json'])
        json.dump(json_obj, open('topic_rules.json', 'w'))
	bucket.upload_file('topic_rules.json', 'topic_rules.json')
	message = "Topic Rules Saved! Processing..."

    return render_template('topics.html', json_obj=json_obj, message=message)
    

@app.route('/products/<asin>')
def products(asin):
    conn = db.get_conn() 
    product = db.fetchone(conn, """
                    select *
                    from products p 
                    where asin = '{asin}'
                    """.format(asin=asin))
    
    q = request.args.get("q", '')
    topic = request.args.get("topic", '')

    filters = "where r.asin = '{}'".format(asin)

    if q:
	query = ' & '.join(re.split('\s+', q.strip()))
        filters += """ and to_tsvector('english', summary || ' ' || "reviewText") @@ to_tsquery('english', '{query}')
""".format(query=query)

    if topic:
    	filters = 'join review_topics t on t.asin = r.asin and t."reviewerID" = r."reviewerID" ' + filters
	filters += """ and t.topic = '{}'""".format(topic)

    reviews_best = db.fetchall(conn, """
                    select *
                    from reviews r 
                    {filters}
                    and sentiment = 1
                    limit 10
                    """.format(filters=filters))

    reviews_worst = db.fetchall(conn, """
                    select *
                    from reviews r 
                    {filters}
                    and sentiment = 0
                    limit 10
                    """.format(filters=filters))

    topics_sentiment = db.fetchall(conn, """
                     select 
			    topic, 
			    sentiment,
			    count(*) 
		    from review_topics t
		    left join reviews r on t.asin = r.asin and t."reviewerID" = r."reviewerID"
		    where t.asin = '{asin}'
		    group by topic, sentiment 
                    """.format(asin=asin))

    reviews_time = db.fetchall(conn, """
	select
                sentiment,
		(cast(extract(year from "reviewTime") as text) || '-' || cast(extract(month from "reviewTime") as text)) as t,
		count(*) 
	from reviews r 
	where r.asin = '{asin}'
	group by sentiment, t
    """.format(asin=asin))

    topic_names = set([t[0] for t in topics_sentiment])

    return render_template('product.html', topics_sentiment=topics_sentiment,
                                           product=product, 
                                           reviews_best=reviews_best,
                                           reviews_worst=reviews_worst,
					   topic_names=topic_names,
                                           q=q,
                                           topic=topic,
					   reviews_time=reviews_time)

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'db_conn'):
    	g.db_conn.close()


if __name__ == '__main__':
    app.run(threaded=True, debug=True, host="0.0.0.0")
