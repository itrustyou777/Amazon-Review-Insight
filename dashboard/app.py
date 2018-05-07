from flask import Flask, render_template, request, g
import db
import boto3
import json

app = Flask(__name__)

@app.route('/')
def index():
    q = request.args.get("q", '')

    products = []

    if q:
        conn = db.get_conn() 
        cursor = conn.cursor()
        cursor.execute("""
                        select *
                        from products p 
                        where title ilike '%{q}%' or brand ilike '%{q}%'
                        order by title
                       """.format(q=q))
        products = cursor.fetchall()

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
	message = "Topic Rules Saved"

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
        filters += """ and ("reviewText" ilike '%{}%' or summary ilike '%{}%')""".format(q, q)

    if topic:
    	filters = 'join review_topics t on t.asin = r.asin and t."reviewerID" = r."reviewerID" ' + filters
	filters += """ and t.topic = '{}'""".format(topic)

    reviews = db.fetchall(conn, """
                    select *
                    from reviews r 
                    {filters}
                    limit 10
                    """.format(filters=filters))

    topics_sentiment = db.fetchall(conn, """
                     select 
			    topic, 
			    case 
			    when overall > 3 then 'positive'
			    when overall <= 3 then 'negative'
			    end as sentiment,
			    count(*) 
		    from review_topics t
		    left join reviews r on t.asin = r.asin and t."reviewerID" = r."reviewerID"
		    where t.asin = '{asin}'
		    group by topic, sentiment 
                    """.format(asin=asin))

    topic_names = set([t[0] for t in topics_sentiment])

    return render_template('product.html', topics_sentiment=topics_sentiment,
                                           product=product, 
                                           reviews=reviews,
					   topic_names=topic_names,
                                           q=q,
                                           topic=topic)

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'db_conn'):
    	g.db_conn.close()

