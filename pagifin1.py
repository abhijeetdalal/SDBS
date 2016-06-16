from flask import Flask, render_template, json, request,redirect,session,jsonify,current_app
from flask import request
from flask.ext.paginate import Pagination
import DbConnection

app = Flask(__name__)

con = DbConnection.dbConnection()

@app.route('/')
@app.route('/index')
def index():
    print "h1"
    page, per_page, offset = get_page_items()
    print "h2"
    with con:
        print "con"
        cur = con.cursor()	
        cnt=cur.execute("SELECT * from fb_post")
        print cnt
        cur.execute("SELECT * from fb_post limit {},{}".format(offset,per_page))
        user = cur.fetchall()
        total=cur.fetchone()
        print user
        pagination = get_pagination(page=page,
                                per_page=per_page,
                                total=cnt,
                                record_name='user',
                                format_total=True,
                                format_number=True,
                                )
        print "hhhhhhhhhhhhhhhhhhelloooooooooo"
    return render_template('facebook_pagination.html', user=user,
                           page=page,
                           per_page=per_page,
                           pagination=pagination,
                           )

 
def get_css_framework():
    return current_app.config.get('CSS_FRAMEWORK', 'bootstrap3')


def get_link_size():
    return current_app.config.get('LINK_SIZE', 'sm')


def show_single_page_or_not():
    return current_app.config.get('SHOW_SINGLE_PAGE', False)


def get_page_items():
    print "item"
    page = int(request.args.get('page', 1))
    per_page = request.args.get('per_page')
    print "page",page,per_page
    print "item"
    if not per_page:
        
        per_page = current_app.config.get('PER_PAGE', 10)
    else:
        per_page = int(per_page)

    offset = (page - 1) * per_page
    print "page",page,per_page
    return page, per_page, offset


def get_pagination(**kwargs):
    kwargs.setdefault('record_name', 'records')
    return Pagination(css_framework=get_css_framework(),
                      link_size=get_link_size(),
                      show_single_page=show_single_page_or_not(),
                      **kwargs
                      )


if __name__ == "__main__":
    app.run(port=5032)
