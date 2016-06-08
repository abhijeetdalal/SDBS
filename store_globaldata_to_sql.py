try:
    import json
    import MySQLdb as mdb
    from sys import argv
except ImportError:
    import simplejson as json

tweets_filename = 't2.txt'
tweets_file = open(tweets_filename, "r")
con = mdb.connect('localhost', 'root', 'admin123', 'SDBS_database');
for line in tweets_file:
    try:
        
        tweet = json.loads(line.strip())
        if 'text' in tweet: 
           
	    with con:
		cur = con.cursor()

		
		cur.execute("INSERT INTO global_tweets(id,created_at,tweets) VALUES(%s,%s,%s)",(tweet['user']['screen_name'],tweet['created_at'],tweet['text'].encode("ascii", "ignore")))
                cur.execute("INSERT INTO current_global_tweets(id,created_at,tweets) VALUES(%s,%s,%s)",(tweet['user']['screen_name'],tweet['created_at'],tweet['text'].encode("ascii", "ignore")))

	    hashtags = []
            for hashtag in tweet['entities']['hashtags']:
            	hashtags.append(hashtag['text'])
           
    except:
        
        continue
with con:
	keyword=argv[1]                  
	cur = con.cursor()
        keyword="%" + keyword + "%"
	print "keyword",keyword
	cur.execute("INSERT INTO filter_global_tweets (id,created_at,tweets) ( select id,created_at,tweets from current_global_tweets where tweets like %s)",(keyword, ))
        #print "stored in sql"
        
        cur.execute("INSERT INTO filter_local_tweets (id,created_at,tweets) ( select id,created_at,tweets from local_tweets where tweets like %s)",(keyword, ))
            
        
