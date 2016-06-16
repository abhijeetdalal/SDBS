import json,requests
import sys,csv,re,os
import time
from time import gmtime, strftime
import multiprocessing
import DbConnection

v=False
outFile=None

ACCESSTOKEN='EAACEdEose0cBANx25ASHSMatAqH3BDzC5SsXvYK4sGhs57jksZCsJ9H2wZBgUllN32KRG7XjJm8RASVxNeqNIWikLsQniWAmZAvlPRXUNSbrSWZBZA5mcgCVGrgdsQntKGbl6Oqzrifli8lz5B0EfyBgciMpCJVCkrl0n6VOOlQZDZD'
con = DbConnection.dbConnection()

LIMIT=sys.argv[2]

print "limit",LIMIT
QUERY=sys.argv[1]
# Query to grab pages
print "Keywords",sys.argv[1]
terms=[QUERY]

regexString='|'.join(terms)
matchRe=re.compile(regexString)
# Construct regex from terms

nMatches=0
nTrash=0

#################
def logQuery(url):
  global logFile

  pageId=url.partition('graph.facebook.com/')[2]
  pageId=pageId.partition('/posts')[0]

#################
def matchesQuery(text,outFile):
  returnVal=False
  res=re.search(regexString,text,re.UNICODE|re.IGNORECASE)
  if res:
    returnVal=True
    
  return returnVal
#################
def parsePosts(rr,nPages,nPosts,category):
  
  global nMatches
  
  for d,dd in enumerate(rr[u'data']):
      nPosts+=1

      try:
        if v:print '\tMESSAGE',dd[u'message'].encode('utf-8')
      except:
        z=0

      if u'message' in dd.keys():
    # Can we use 'story' entries?
        message=dd['message'].encode('utf-8')
	id1=dd[u'id']
        #print id1
	
        cat=dd[u'created_time']
        with con:
            cur = con.cursor()
	    
            cur.execute("INSERT INTO fb_post(id,created_at,comment) VALUES(%s,%s,%s)",((id1,cat,message)))
	    cur.execute("DELETE FROM fb_post where comment not like %s",(('%'+QUERY+'%')))    

        outLine=['POST',dd[u'id'],dd[u'created_time']]
        outLine.append(message.replace('\n',' | '))
        outLine.append(category)
        if v:print 'MATCHES?'
        if matchesQuery(dd['message'],outFile):
          
          nMatches+=1
      else:
        if v:print '!!! NO MESSAGE',dd.keys()

      if v: print 'COMMENTS?'

      if u'comments' in dd.keys():
       
        for c in dd['comments']['data']:
          if v:print '\t\tCOMMENT',c['message']
          message=c['message'].encode('utf-8')
	  id3=c[u'id']
	  cat=c[u'created_time']
	  with con:
            cur = con.cursor()
            
	    cur.execute("INSERT INTO fb_post(id,created_at,comment) VALUES(%s,%s,%s)",((id3,cat,message)))
	    cur.execute("DELETE FROM fb_post where comment not like %s",(('%'+QUERY+'%')))   
          outLine=['COMMENT',c[u'id'],c[u'created_time']]
          outLine.append(re.sub('\n',' | ',message))
          outLine.append(category)
   
      else:
        if v:print '!!! NO COMMENTS',dd.keys()

      if v:print '+++++++++++++++++++'
  if v:print ''
  nPages+=1

  return nPages,nPosts

def main():

  restartOffset=0
  nPostsTotal=0
  # Counts total number of unfiltered posts considered
  nMatchesTotal=0
  global nMatches

  startTime=time.localtime()
  
  skip=False
  commentsPageSkip=False
  restartCommentsPage=None
  restartId=-9999
 
  tempUrl='https://graph.facebook.com/search?q='+QUERY+'&limit='+LIMIT+'&type=page&access_token='+ACCESSTOKEN
  r=requests.get(tempUrl).json()
  logQuery(tempUrl)
# Get all pages matching QUERY

  if not 'data' in r.keys():
    print 'EXPIRED????',r
    sys.exit(1)

  for p,page in enumerate(r[u'data']):

    errorSkip=False
    nError=0

    try:
      print 'PAGE #',p,'('+str(len(r[u'data']))+')',page[u'name'],page[u'category'],page[u'id'],strftime("%H:%M:%S", time.localtime())
    except:
      print '!!!!!!!PAGE ERROR'

    if page[u'id']==restartId:
      skip=False
      print 'RESTARTING....'

    if not skip:
      tempUrl='https://graph.facebook.com/'+page[u'id']+'/posts?'+'&limit='+LIMIT+'&access_token='+ACCESSTOKEN
      logQuery(tempUrl)
      rr=requests.get(tempUrl).json()
      # Try to get the posts

      while u'error' in rr.keys() or u'error_msg' in rr.keys():
        if (u'error' in rr.keys() and u'code' in rr[u'error'].keys() and rr[u'error'][u'code'] in [1,2]) or u'error_msg' in rr.keys():
        # API error
          print 'API ERROR: SLEEPING....'
          print rr
          time.sleep(60)
          print 'RETRYING (1)'
          nError+=1
          if nError==10:
            print nError,'ERRORS - SKIPPING'
            errorSkip=True
            break
        else:
        # TOKEN ERROR
          print '********ERROR',rr[u'error']
          sys.exit(1)
        tempUrl='https://graph.facebook.com/'+page[u'id']+'/posts?'+'&limit='+LIMIT+'&access_token='+ACCESSTOKEN
        rrtemp=requests.get(tempUrl)
        print 'rrtemp',rrtemp,rrtemp.text
        rr=rrtemp.json()
        logQuery(tempUrl)
        # Try to get the posts again

      nPages=0
      nError=0
      nPosts=0
      nMatches=0

      if not errorSkip and not commentsPageSkip:
      # If API has caused 3 errors, skip
      # Or if restarting from a later comments page, skip
        errorSkip=False
        nPages,nPosts=parsePosts(rr,nPages,nPosts,page[u'category'].encode('utf-8'))

      while 'paging' in rr.keys() and not errorSkip and not commentsPageSkip:

        if v:print 'LOADING',rr[u'paging'][u'next']

        rrrRaw=requests.get(rr[u'paging'][u'next'])
        logQuery(rr[u'paging'][u'next'])

        if rr['paging']['next']==restartCommentsPage and restartCommentsPage:
          commentsPageSkip=False
          print '**********MATCHED RESTART PAGE - RESUMING PARSING COMMENTS'
        # If we want to restart from last page
        elif restartCommentsPage and restartId==page['id']:
          print '**********DIDNT MATCH COMMENTS RESTART PAGE'
          restartOffset+=1

        try:
          rrr=rrrRaw.json()
        except:
          print 'JSON ERROR', rrrRaw.status_code

        while u'error' in rrr.keys() or u'error_msg' in rrr.keys():

          if u'error' in rrr.keys() or u'error_msg' in rrr.keys():
          # API error
            print 'API ERROR: SLEEPING....'
            print rrr,rrrRaw,rrrRaw.status_code,rrrRaw.text
            print rr[u'paging'][u'next']
            time.sleep(10)
            print 'RETRYING'
            nError+=1
            if nError==10:
              print nError,'ERRORS - SKIPPING'
              errorSkip=True
              break
          else:
          # TOKEN ERROR ?
            print '********ERROR',rrr
            sys.exit(1)

          rrr=requests.get(rr[u'paging'][u'next'])
          rrr=rrr.json()
          logQuery(rr['paging']['next'])

        if not commentsPageSkip:
          if v:
            print '# COMMENTS PAGES',nPages,'# POSTS',nPosts,'# MATCHES',nMatches,strftime("%H:%M:%S", time.localtime()),
            if not restartOffset==0:
              print '# OFFSET',restartOffset
            else:
              print ''

        if (not errorSkip and not commentsPageSkip) and not skip:
          nPages,nPosts=parsePosts(rrr,nPages,nPosts,page[u'category'].encode('utf-8'))
        else:
          print '************NOT PARSING POSTS',errorSkip,commentsPageSkip
          print 'BREAKING'
          break
        rr=rrr
      print '# COMMENTS PAGES',nPages,'# POSTS',nPosts,'# MATCHES',nMatches,strftime("%H:%M:%S", time.localtime())
      if not restartOffset==0:
        print '# OFFSET',restartOffset
      
      nPostsTotal+=nPosts
      nMatchesTotal+=nMatches
      print 'TOTAL SO FAR #POSTS',nPostsTotal,'#MATCHES',nMatchesTotal
      print '-----------'
      restartOffset=0
    else:
      print ' ',nPostsTotal
  print 'FINISHED',strftime("%H:%M:%S",startTime),'-',strftime("%H:%M:%S",time.localtime())


if __name__=='__main__':

  #main()
  p = multiprocessing.Process(target=main, name="main", args=())
  p.start()

  time.sleep(100)

  # Terminate foo
  p.terminate()

  # Cleanup
  p.join()


