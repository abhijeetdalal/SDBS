import json
from sys import argv
import simplejson as json
import DbConnection

tweets_filename = 't2.txt'
tweets_file = open(tweets_filename, "r")
con = DbConnection.dbConnection()

with con:
	cur = con.cursor()
	cur.execute("delete from global_tweets")
	cur.execute("delete from current_global_tweets")
	cur.execute("delete from filter_global_tweets")
	cur.execute("delete from filter_local_tweets")

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
	maxcount=argv[1]
	keyword=argv[2]                  
	cur = con.cursor()
        keyword="%" + keyword + "%"
	sql_filter_global_tweets = "INSERT INTO filter_global_tweets (id,created_at,tweets) ( select id,created_at,tweets from current_global_tweets where tweets like '"+keyword+"' limit "+maxcount+")";
	sql_filter_local_tweets = "INSERT INTO filter_local_tweets (id,created_at,tweets) ( select id,created_at,tweets from local_tweets where tweets like '"+keyword+"' limit "+maxcount+")";
	cur.execute(sql_filter_global_tweets)
        cur.execute(sql_filter_local_tweets)
            
        
