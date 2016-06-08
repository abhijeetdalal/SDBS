from sys import argv
import MySQLdb as mdb
import sys
import time
import cPickle
import twitter
from twitter.oauth_dance import oauth_dance

con = mdb.connect('localhost', 'root', 'admin123', 'SDBS_database');
with con:
        cur = con.cursor()
        cur.execute("SELECT * from twitter_api_key")
	data=cur.fetchall()    
        for d in data:       
            oauth_token = d[0]
            oauth_token_secret = d[1]
            consumer_key = d[2]
            consumer_secret = d[3]
"""
consumer_key ='AKhqB5TBYqSBqQXvMksWIZlsQ'
consumer_secret='8qsGhKlUyuucHqwlIl7jFW2BWzjqGMzwcesottz1YPJl4N0TQD'
oauth_token='3568557440-rRAVNTs3aLesqPmj94RGPRn4lhTzYYllopgjJeN'
oauth_token_secret='jWrKAYgMPBo5ImUBCmskXKX8lhcgpJ1KnWFUnsiEvVci4'

consumer_key ='W8GOQRVCObV0e9nERvd0afkoc'
consumer_secret='A5LFFftmw4hsKjbY4J4YyqahSSav9FlttZcOM57bsRIqKNipmD'
oauth_token='3568557440-CBr50k520XVYOxASug2KX6jIFPA788lRqi5VbAr'
oauth_token_secret='uy0XzON4N8pwOnk33Ub6wRkh1mQMhrSVb5Bz5PqaAWErd'
"""

t = twitter.Twitter(domain='api.twitter.com', api_version='1.1',
                    auth=twitter.oauth.OAuth(oauth_token, oauth_token_secret,
                    consumer_key, consumer_secret))


def gettweets(id2):
  
    user = id2
  
    results = t.statuses.user_timeline(user_id = user)
    with con:
        cur = con.cursor()

    for status in results:
        
        cur.execute("INSERT INTO local_tweets(id,created_at,tweets) VALUES(%s,%s,%s)",(status["user"]["screen_name"],status["created_at"],status["text"].encode("ascii", "ignore")))
        
       
def getid(id1,ids2,ids3,cnt):
	
	id2=id1
	friends_limit = 5
	ids=[]
	wait_period = 2  
	cursor = -1
        d=len(ids3)
	
        for i in range(0,len(ids3)):
                id2=ids2[cnt]
		if id2 in ids3:
			cnt+=1
	
	for i in range(0,cnt):
        	id2=ids2[cnt] 
      
	gettweets(id2)
	while cursor != 0:
	    if wait_period > 3600:  
		print 'Too many retries. Saving partial data to disk and exiting'
		f = file('%s.followers_ids' % str(cursor), 'wb')
		cPickle.dump(ids, f)
		f.close()
		exit()

	    try:
		response = t.followers.ids(user_id=id2, cursor=cursor)
		ids.extend(response['ids'])
		ids2.extend(response['ids'])
                
		wait_period = 5
	    except twitter.api.TwitterHTTPError, e:
		if e.e.code == 401:
		    print 'Encountered 401 Error (Not Authorized)'
		    print 'User %s is protecting their tweets' % (SCREEN_NAME, )
		elif e.e.code in (502, 503):
		    print 'Encountered %i Error. Trying again in %i seconds' % (e.e.code,
		            wait_period)
		    time.sleep(wait_period)
		    wait_period *= 1.5
		    continue
		elif t.account.rate_limit_status()['remaining_hits'] == 0:
		    status = t.account.rate_limit_status()
		    now = time.time()  # UTC
		    when_rate_limit_resets = status['reset_time_in_seconds']  # UTC
		    sleep_time = when_rate_limit_resets - now
		    print 'Rate limit reached. Trying again in %i seconds' % (sleep_time,
		            )
		    time.sleep(sleep_time)
		    continue

	    cursor = response['next_cursor']
	    
	    if len(ids) >= friends_limit:
		break
	ids3.append(id2)
	
	for i in range(0,len(ids2)):
		    cnt +=1
		    
		    getid(ids2[cnt],ids2,ids3,cnt)       
	


if (len(sys.argv) ==1):
        with con:
            
            cur = con.cursor()
            cur.execute("select id from twitter_id");
            data=cur.fetchall()    
            for d in data:       
                n = d[0]
            id1=n
            print id1
            
else:
	id1 = argv[1]

ids2=[ ]
ids2.append(id1)
ids3= []
cnt=0
getid(id1,ids2,ids3,cnt)



