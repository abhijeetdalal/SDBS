from flask import Flask, render_template, json, request,redirect,session,jsonify,current_app,url_for
from twython import Twython
from werkzeug import generate_password_hash, check_password_hash
import os,sys,csv,time
from flask import request
from flask.ext.paginate import Pagination
import DbConnection

app = Flask(__name__)

con = DbConnection.dbConnection()

@app.route('/')
def main():
    tablecreation()
    return render_template('homepage.html')


@app.route('/tablecreation')
def tablecreation():
    with con:
        cur = con.cursor()
        cur.execute("CREATE DATABASE IF NOT EXISTS SDBS_database")
	cur.execute("USE SDBS_database")
        cur.execute("CREATE TABLE IF NOT EXISTS local_tweets(id varchar(500),created_at varchar(500),tweets varchar(500))")
        cur.execute("CREATE TABLE IF NOT EXISTS global_tweets(id varchar(500),created_at varchar(500),tweets varchar(500))")

        cur.execute("CREATE TABLE IF NOT EXISTS current_global_tweets(id varchar(500),created_at varchar(500),tweets varchar(500))")
        cur.execute("CREATE TABLE IF NOT EXISTS filter_global_tweets(id varchar(500),created_at varchar(500),tweets varchar(500))")

        cur.execute("CREATE TABLE IF NOT EXISTS filter_local_tweets(id varchar(500),created_at varchar(500),tweets varchar(500))")

        cur.execute("CREATE TABLE IF NOT EXISTS signup(username varchar(500) primary key,password varchar(500),created_at varchar(500),question varchar(500),answer varchar(500))")

        cur.execute("CREATE TABLE IF NOT EXISTS fb_post(id varchar(500),created_at varchar(1000),comment varchar(25000))")

        cur.execute("CREATE TABLE IF NOT EXISTS twitter_id(id double)")
        cur.execute("delete from twitter_id")
        
        cur.execute("insert into twitter_id values(3745729752)")
        
        cur.execute("CREATE TABLE IF NOT EXISTS twitter_api_key(oauth_token varchar(500),oauth_token_secret varchar(500),consumer_key varchar(500),consumer_secret varchar(500))")


        cur.execute("delete from twitter_api_key") 

        cur.execute("insert into twitter_api_key values('3568557440-CBr50k520XVYOxASug2KX6jIFPA788lRqi5VbAr','uy0XzON4N8 pwOnk33Ub6wRkh1mQMhrSVb5Bz5PqaAWErd','W8GOQRVCObV0e9nERvd0afkoc', 'A5LFFftmw4hsKjbY4J4YyqahSSav9FlttZcOM57bsRIqKNipmD')")

        cur.execute("CREATE TABLE IF NOT EXISTS facebook_api_key(access_token varchar(5000))")

        cur.execute("insert into facebook_api_key values('EAAYDhVZBtqU4BADsMiigsaZClhd8kZADdMx86XBoAMI1ZAgxGkAI xHL7mlNFavby8j9fJ29pj8CKfZCYbvXZCZB7rzPOZB2dZCKQLoG9OQk1urV4LjLBKMUrFBzq 3eyTGzPMSCuJbJYT6f3JPsJhpI9AGYS2IJhQlI ZAnSED5oJHPOYgZDZD')")

@app.route('/home_render', methods=['POST','GET'])
def home_render():
    return render_template('homepage.html')

@app.route('/signUp', methods=['POST','GET'])
def signUp():
    return render_template('signup.html')

@app.route('/Loginrender' , methods=['POST','GET'])
def Loginrender():
    return render_template('login.html')

@app.route('/helprender' , methods=['POST','GET'])
def helprender():
    return render_template('help.html')
 
@app.route('/backtotwitter' , methods=['POST','GET'])
def backtotwitter():
    return render_template('twitter_main.html')
    
@app.route('/Login' , methods=['POST','GET'])
def Login():
    email=request.form['username']
    passwd=request.form['pwd1']
    flag=0
    with con:
        cur = con.cursor()
        cur.execute("SELECT * from signup")
	num=int(cur.rowcount)

	for i in range (num):
            row = cur.fetchone()
            if (row):
                if(email==row[0] and passwd==row[1]):
                    flag=1
                   
        if(flag==1):
            return render_template('social_media_option.html')
                   
                    
        else:
            return render_template('login.html',error = 'Wrong Email address or Password.')
        

@app.route('/check_selected_media_options' , methods=['POST'])
def check_selected_media_options():
    n=request.form['radiog_lite']
   
    if(n=="0"):
        return render_template('twitter_main.html')
        
    elif(n=="1"):
        return render_template('facebook_main.html')    
    else:
        return render_template('social_media_option.html')    


@app.route('/twit_details' , methods=['POST','GET'])
def twit_details():
    keyword = request.form['keyword2']
    linkid=request.form['rcheck']
    twitid=request.form['twitterid']
    maxcnt=request.form['maxcount']
    if(maxcnt!=''):
		maxcnt=int(maxcnt)	
    button=request.form['btn']	
    counts = []
    with con:
        cur = con.cursor()
        cur.execute("delete from filter_global_tweets")
        cur.execute("delete from filter_local_tweets")
   
    if (linkid=="0" and button=="BehavioralSearch"):
        for d in csv.DictReader(open('csv\\'+keyword+'.csv'), delimiter='\t'):
			counts.append((d[keyword])) 
    
        os.system(("python linking_through_twitid.py") )
	for i in range(0,len(counts)):
		os.system(("python globalsearch.py {} {}".format(maxcnt,counts[i])) ) 
		os.system(("python store_globaldata_to_sql.py {} {}".format(maxcnt, counts[i])) )
	return redirect(url_for('twitpagination'))            
    
    if (linkid=="1" and button=="BehavioralSearch"):
        for d in csv.DictReader(open(keyword+'.csv'), delimiter='\t'):
			counts.append((d[keyword])) 
	os.system(("python linking_through_twitid.py {}".format(twitid)) )
	for i in range(0,len(counts)):
		os.system(("python globalsearch.py {} {}".format(maxcnt,counts[i])) ) 
		os.system(("python store_globaldata_to_sql.py {} {}".format(maxcnt, counts[i])) )
	return redirect(url_for('twitpagination'))
	
    if (linkid=="0" and button=="DirectSearch"):
        os.system(("python linking_through_twitid.py") )
        os.system(("python globalsearch.py {} {}".format(maxcnt,'"'+keyword+'"')) ) 
	os.system(("python store_globaldata_to_sql.py {} {}".format(maxcnt,'"'+keyword+'"')) )
        return redirect(url_for('twitpagination'))
       
        
    if (linkid=="1" and button=="DirectSearch"):
        os.system(("python linking_through_twitid.py {}".format(twitid)) )
	os.system(("python globalsearch.py {} {}".format(maxcnt,'"'+keyword+'"')) ) 
	os.system(("python store_globaldata_to_sql.py {} {}".format(maxcnt,'"'+keyword+'"')) )
        return redirect(url_for('twitpagination'))

    if (button=="Cancel"):
        return render_template('social_media_option.html')


@app.route('/twitpagination' , methods=['POST','GET'])
def twitpagination():
    page, per_page, offset = get_page_items()
    with con:
        cur = con.cursor()	
        cnt=cur.execute("SELECT * from filter_global_tweets")
        cur.execute("SELECT * from filter_global_tweets limit {},{}".format(offset,per_page))
        user = cur.fetchall()
        total=cur.fetchone()
        pagination = get_pagination(page=page,
                                per_page=per_page,
                                total=cnt,
                                record_name='user',
                                format_total=True,
                                format_number=True,
                                )
    
    return render_template('results.html', user=user,
                           page=page,
                           per_page=per_page,
                           pagination=pagination,
                           )        

#@app.route('/get_page_items' , methods=['POST','GET'])
def get_page_items():

    page = int(request.args.get('page', 1))
    per_page = request.args.get('per_page')
    if not per_page:		
        per_page = current_app.config.get('PER_PAGE', 10)
    else:
        per_page = int(per_page)
    offset = (page - 1) * per_page
    return page, per_page, offset
                   
     
@app.route('/get_css_framework' , methods=['POST','GET'])
def get_css_framework():
    return current_app.config.get('CSS_FRAMEWORK', 'bootstrap3')

@app.route('/get_link_size' , methods=['POST','GET'])
def get_link_size():
    return current_app.config.get('LINK_SIZE', 'sm')

@app.route('/show_single_page_or_not' , methods=['POST','GET'])
def show_single_page_or_not():
    return current_app.config.get('SHOW_SINGLE_PAGE', False)

@app.route('/get_pagination' , methods=['POST','GET'])
def get_pagination(**kwargs):
    kwargs.setdefault('record_name', 'records')
    return Pagination(css_framework=get_css_framework(),
		              link_size=get_link_size(),
		              show_single_page=show_single_page_or_not(),
		              **kwargs
		              )


@app.route('/checksignUp' , methods=['POST','GET'])

def checksignUp():
    email=request.form['username']
    ans1=request.form['ans']
    passwd=request.form['pwd1']
    question=request.form['role']
    timeat1=time.ctime()
    print timeat1,question
    flag=0
    with con:
        cur = con.cursor()
        cur.execute("SELECT * from signup")
	num=int(cur.rowcount)
        print num
	for i in range (num):
            row = cur.fetchone()
            print row
            if (row):
                if(email==row[0]):
                    flag=1
                   
        if(flag==1):
            return render_template('signup.html',error = 'User already exist.')
                   
                    
        else:
            print "***********************"
            if (question=="1"):
                print "with"
                with con:
                    ques="What is your birth place"
                    cur = con.cursor()
                    cur.execute("INSERT INTO signup(username,password,created_at,question,answer) VALUES(%s,%s,%s,%s,%s)",((email),(passwd),(timeat1),(ques),(ans1)))

            elif (question=="2"):
                with con:
                    ques="What is your nick name"
		cur = con.cursor()

		cur.execute("INSERT INTO signup(username,password,created_at,question,answer) VALUES(%s,%s,%s,%s,%s)",((email),(passwd),(timeat1),(ques),(ans1)))
	  
            elif (question=="3"):
	      with con:
                    ques="What was name of your first pet"
                    cur = con.cursor()

                    cur.execute("INSERT INTO signup(username,password,created_at,question,answer) VALUES(%s,%s,%s,%s,%s)",((email),(passwd),(timeat1),(ques),(ans1)))
	  
    return render_template('login.html')

@app.route('/forgetpassword' , methods=['POST','GET'])
def forgetpassword():
    return render_template('forget_pass.html')

@app.route('/screen_name' , methods=['POST','GET'])
def screen_name():
    return render_template('screen_name.html')

@app.route('/get_twitter_id' , methods=['POST','GET'])
def get_twitter_id():
    app_key = 'o2364QzhfTxjCCwZ6guKTPN4i'
    app_secret ='JGwxQzbtLGsIu2HXV4f2T1GALgKrNm7O7wdZs6xBzoMZVnWksZ'
    oauth_token = '3568557440-z3V9Ki4eptgt09nAnUhCPtF8eYy3btN2jR9QNBM'
    oauth_token_secret= 'qPR9BlhPcLxvnRO6AETMoBo0eZaF1DP0CF4fYbUqaN9E7'

    twitter = Twython(app_key, app_secret, oauth_token, oauth_token_secret)
    ids=request.form['scname']
    
    output = twitter.lookup_user(screen_name=ids)
 
    for user in output:
        twitid=user["id_str"]
	
    return render_template('twitter_main.html',var=twitid)  	   

@app.route('/recovery_ans_check' , methods=['POST','GET'])
def recovery_ans_check():
    user=request.form['username']
    ans1=request.form['ans']
    question=request.form['role']
    flag=0
    if (question=="1"):
	ques="What is your birth place"
        with con:
            cur = con.cursor()
            
            cur.execute("SELECT * from signup")
            num=int(cur.rowcount)
            print num
	    for i in range (num):
                row = cur.fetchone()
                print row
                if (row):
                    if(user==row[0] and ques==row[3]):
                        if(ans1==row[4] or ans1==(row[4].upper()) or ans1==(row[4].capitalize()) or ans1==(row[4].lower())):
		            flag=1
                                       
            if(flag==1):
                return render_template('reset_pass.html')
                   
                    
            else:
	        return render_template('forget_pass.html')
                    
       
            
    if (question=='2'):
        ques="What is your nick name"
        with con:
            cur = con.cursor()
            
            cur.execute("SELECT * from signup")
            num=int(cur.rowcount)
            print num
	    for i in range (num):
                row = cur.fetchone()
                print row
                if (row):
                    if(user==row[0] and ques==row[3]):
                        if(ans1==row[4] or ans1==(row[4].upper()) or ans1==(row[4].capitalize())):
		            flag=1
                                                           
            if(flag==1):
                return render_template('reset_pass.html')
                   
                    
            else:
	        return render_template('forget_pass.html')
                    
        
    if (question=='3'):
        ques="What was your first pet name"
        with con:
            cur = con.cursor()
            
            cur.execute("SELECT * from signup")
            num=int(cur.rowcount)
            print num
	    for i in range (num):
                row = cur.fetchone()
                print row
                if (row):
                    if(user==row[0] and ques==row[3]):
                        if(ans1==row[4] or ans1==(row[4].upper()) or ans1==(row[4].capitalize())):
		            flag=1
                                                           
            if(flag==1):
                return render_template('reset_pass.html')
                   
                    
            else:
	        return render_template('forget_pass.html')
                    
        
@app.route('/reset_password_store' , methods=['POST','GET'])
def reset_password_store():
    user=request.form['username']
    pass1=request.form['pwd1']
    timeat1=time.ctime()
    print timeat1
    with con:
        cur = con.cursor()	
     
        cur.execute("update signup set password=%s,created_at=%s where username=%s ",((pass1),(timeat1),(user)))
        
    return render_template('login.html') 

@app.route('/fb_details' , methods=['POST','GET'])
def fb_details():
    keyword = request.form['fbkeyword']
    maxcnt=int(request.form['fbmaxcnt'])
    button=request.form['btn']
    if(button=="DirectSearch"):
  
	keyword="'"+keyword+"'"
	print "key:",keyword

        os.system(("python fb_global.py {} {} ".format((keyword),(maxcnt))) )         
        page, per_page, offset = get_page_items()
        with con:
            cur = con.cursor()	
            cnt=cur.execute("SELECT * from fb_post")
            print "*********************************"
            cur.execute("SELECT * from fb_post limit {},{}".format(offset,per_page))
            user = cur.fetchall()
            total=cur.fetchone()
            print "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&"
            pagination = get_pagination(page=page,
                                per_page=per_page,
                                total=cnt,
                                record_name='user',
                                format_total=True,
                                format_number=True,
                                )
        os.system("python pagifin1.py")

    if (button=="Cancel"):
        
        return render_template('facebook_main.html')

    if(button=="BehaviorSearch"):
        for d in csv.DictReader(open(keyword+'.csv'), delimiter='\t'):
            counts.append((d[keyword])) 
    	
	for i in range(0,len(counts)):
            os.system(("python fb_global.py {} {}".format((counts[i]),(maxcnt))) ) 

	with con:
            cur = con.cursor()	
            cnt=cur.execute("SELECT * from fb_post")
            cur.execute("SELECT * from fb_post limit {},{}".format(offset,per_page))
            user = cur.fetchall()
            total=cur.fetchone()
            pagination = get_pagination(page=page,
                                per_page=per_page,
                                total=cnt,
                                record_name='user',
                                format_total=True,
                                format_number=True,
                                )
        os.system("python pagifin1.py")

            
    return render_template('social_media_option.html') 
  
if __name__ == "__main__":
    app.run(port=5034)

