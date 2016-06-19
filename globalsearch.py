import tweepy
from sys import argv
import sys
import jsonpickle
import os
import DbConnection


con = DbConnection.dbConnection()
with con:
        cur = con.cursor()
        cur.execute("SELECT * from twitter_api_key")
        data=cur.fetchall()    
        for d in data:       
            API_KEY = d[2]
            API_SECRET = d[3]

auth = tweepy.AppAuthHandler(API_KEY,API_SECRET )
 
api = tweepy.API(auth, wait_on_rate_limit=True,
				   wait_on_rate_limit_notify=True)
 
if (not api):
    print ("Can't Authenticate")
    sys.exit(-1)
keyword=(argv[2]) 
maxcnt=int(argv[1])

searchQuery = keyword
maxTweets = maxcnt 
tweetsPerQry = 100  
fName = 't2.txt' 

sinceId = None
max_id = -1L

tweetCount = 0
print("globalsearch.py, Downloading max {0} tweets".format(maxTweets))
with open(fName, 'w') as f:
    while tweetCount < maxTweets:
        try:
            if (max_id <= 0):
                if (not sinceId):
                    new_tweets = api.search(q=searchQuery, count=tweetsPerQry)
                else:
                    new_tweets = api.search(q=searchQuery, count=tweetsPerQry,
                                            since_id=sinceId)
            else:
                if (not sinceId):
                    new_tweets = api.search(q=searchQuery, count=tweetsPerQry,
                                            max_id=str(max_id - 1))
                else:
                    new_tweets = api.search(q=searchQuery, count=tweetsPerQry,
                                            max_id=str(max_id - 1),
                                            since_id=sinceId)
            if not new_tweets:
                print("No more tweets found")
                break
            for tweet in new_tweets:
                f.write(jsonpickle.encode(tweet._json, unpicklable=False) +
                        '\n')
            tweetCount += len(new_tweets)
            max_id = new_tweets[-1].id
        except tweepy.TweepError as e:
            print("globalsearch.py, Error : " + str(e))
            break