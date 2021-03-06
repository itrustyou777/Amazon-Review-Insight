from flask import Flask, render_template, request, g
from huey.contrib.minimal import MiniHuey
from gevent import monkey; monkey.patch_all()
import db
import boto3
import json
import re
import time
import os

# task queue for incremental processing runs
huey = MiniHuey(pool_size=1)
huey.start()

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
                        where to_tsvector('english', title) @@ to_tsquery('english', {query})
                        limit 15 
                       """.format(query=db.quote(query)))

    return render_template('index.html', q=q, products=products)

@app.route('/talk')
def talk():
    return render_template('talk.html')

@huey.task()
def start_incremental_processing():
    """This is going to run asynchronous in a the huey queue
    """
    os.system(os.path.expanduser("cd ~/ && ./incremental_processing.sh"))

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

        async_result = start_incremental_processing()

    return render_template('topics.html', json_obj=json_obj, message=message)
    

@app.route('/products/<asin>')
def products(asin):
    conn = db.get_conn() 
    product = db.fetchone(conn, """
                    select *
                    from products p 
                    where asin = {asin}
                    """.format(asin=db.quote(asin)))
    
    q = request.args.get("q", '')
    topic = request.args.get("topic", '')

    filters = "where r.asin = {}".format(db.quote(asin))

    if q:
	query = ' & '.join(re.split('\s+', q.strip()))
        filters += """ and to_tsvector('english', summary || ' ' || "reviewText") @@ to_tsquery('english', {query})
""".format(query=db.quote(query))

    if topic:
    	filters = 'join review_topics t on t.asin = r.asin and t."reviewerID" = r."reviewerID" ' + filters
	filters += """ and t.topic = {}""".format(db.quote(topic))

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
		    where t.asin = {asin}
		    group by topic, sentiment 
                    """.format(asin=db.quote(asin)))

    reviews_time = db.fetchall(conn, """
	select
                sentiment,
		(cast(extract(year from "reviewTime") as text) || '-' || cast(extract(month from "reviewTime") as text)) as t,
		count(*) 
	from reviews r 
	where r.asin = {asin}
	group by sentiment, t
    """.format(asin=db.quote(asin)))

    topic_names = set([t[0] for t in topics_sentiment])


    def sort_key(row):
        t = row[1].split('-')

        return (int(t[0]), int(t[1]))

    reviews_time = sorted(reviews_time, key=sort_key)

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
