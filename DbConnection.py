from flask.ext.mysql import MySQL
import MySQLdb as mdb

mysql = MySQL()

def dbConnection():
    con = mdb.connect('localhost', 'root', 'admin123')
    return con