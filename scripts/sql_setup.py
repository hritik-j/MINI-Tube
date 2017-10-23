import MySQLdb
 
db = MySQLdb.connect("localhost","root","shashank","db_videos" )
cursor = db.cursor()
cursor.execute("DROP TABLE IF EXISTS userdata")
sql = """CREATE TABLE userdata (
         first_name  CHAR(30) NOT NULL,
         last_name  CHAR(30) NOT NULL,
         email CHAR(50),
         sex CHAR(10),
         username CHAR(50) PRIMARY KEY,
         password CHAR(20))"""
 
cursor.execute(sql)
 
cursor.execute("DROP TABLE IF EXISTS history")
sql = """CREATE TABLE history(
        s_no INT NOT NULL AUTO_INCREMENT, username CHAR(50),video_id CHAR(100),
        viewed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,primary key(s_no))"""
 
cursor.execute(sql)
 
cursor.execute("DROP TABLE IF EXISTS video_comment")
sql = """CREATE table video_comment( s_no INT NOT NULL AUTO_INCREMENT, username char(50), video_id char(50),
         comment_given text, commented_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, primary key(s_no));"""
 
cursor.execute(sql)
 
 
db.close()