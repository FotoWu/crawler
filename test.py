import pymysql

db = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='root', db='zhihu')
cur = db.cursor()
cur.execute("select * from users")
