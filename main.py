from flask import Flask
from flask import render_template, request, session, redirect, url_for
import MySQLdb
from utilities import *
import json
from graph_utils import *
from recommend import related_videos

graph = Graph(host="localhost",port=7474,password='civilwargnr')


app = Flask(__name__)
app.secret_key = '&$Secret&$Key&$'

db = MySQLdb.connect("localhost","root","hritik","db_videos" )
# graph = Graph(host="localhost",port=7474,password="civilwargnr")

cursor = db.cursor()



@app.route('/',methods = ['POST', 'GET'])
def index():
    session_status = False
    user_details = {'liked':False,'dislike':False}
    if 'username' in session:
        session_status = True
    if request.method == 'GET':
        v_details = None
        q = request.args.get('q')
        v = request.args.get('v')
        p = request.args.get('p')
        v_details = None
        user_playlist = []
        if v:
            v_details = get_details(v)
            video = {"videoId":v}
            v_recommended = get_videos_from_list(related_videos(graph,video,10))
            if session_status:
                user = {'username':session['username']}
                user_details['liked'] = is_like_video(graph,user,video)
                user_details['disliked'] = is_dislike_video(graph,user,video)
                user_playlist = get_owned_playlists(graph,user)
            # print v_recommended
        if not p:
            p = 0
        q_results = None
        if q and v:
            q_results = q_search(q = q,p = int(p))
            return render_template("index.html",q = q, v = v, q_results = q_results, session_status = session_status, v_details = v_details, v_recommended = v_recommended, user_details = user_details ,user_playlist=user_playlist )
        if q and not v:
            q_results = q_search(q = q,p = int(p))
            return render_template('searchResult.html',q = q, q_results = q_results, session_status = session_status)
        if not q and not v:
            v='5RRIQvViQw0'
            video = {"videoId":v}
            v_recommended = get_videos_from_list(related_videos(graph,video,10))
            return render_template('mainpage.html', v = v,session_status = session_status,v_recommended = v_recommended)
        if v and not q:
            return render_template("index.html",q = q, v = v, q_results = q_results, session_status = session_status, v_details = v_details, v_recommended = v_recommended, user_details = user_details , user_playlist=user_playlist)

# @app.route('/test',methods = ['POST', 'GET'])
# def test():
#     session_status = False
#     if 'username' in session:
#         session_status = True
#     if request.method == 'GET':
#         q = request.args.get('q')
#         v = request.args.get('v')
#         p = request.args.get('p')
#         if not p:
#             p = 0
#         q_results = None
#         if q:
#             q_results = q_search(q = q,p = int(p))
#         return render_template("videopage.html",q = q, v = v, q_results = q_results, session_status = session_status )

@app.route('/login/',defaults={'error_msg': ''})
@app.route('/login/<error_msg>')
def login(error_msg):
    if 'username' in session:
        return redirect(url_for('index'))
    return render_template('login.html',error_msg = error_msg)

@app.route('/authenticate', methods=['GET', 'POST'])
def authenticate():
    if 'username' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username  = request.form['username']
        password  = request.form['password']

        sql="SELECT count(*) FROM userdata where username='%s'and password='%s'" % (username,password)
        cursor.execute(sql)

        if cursor.fetchone()[0]==1:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return redirect(url_for('login',error_msg = 'authFail' ))
    return redirect(url_for('login'),error_msg = 'unauthAccess')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'username' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        firstname  = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        gender = request.form['gender']
        username = request.form['username']
        password = request.form['password']

        if username=='' or password=='' or gender=='' or email=='' or firstname=='' or lastname=='':
            return redirect(url_for('login',error_msg = 'fieldEmpty' ))
        else:
            sql="SELECT count(*) from userdata where username='%s'" % (username)
            cursor.execute(sql)
            if cursor.fetchone()[0]==1:
                return redirect(url_for('login',error_msg = 'userExist' ))
            else:
                sql = "INSERT INTO userdata(first_name,last_name,email,sex,username,password) VALUES ('%s', '%s', '%s', '%s', '%s', '%s')" %(firstname,lastname,email,gender,username,password) 
                try:
                    cursor.execute(sql)
                    db.commit()
                    session['username'] = username
                    user = {'username':username,'sex':gender}
                    create_user(graph,user)
                    return redirect(url_for('index'))

                except:
                    # Rollback in case there is any error
                    db.rollback()
                    return redirect(url_for('login'),error_msg = 'regFail')

    return redirect(url_for('login'),error_msg = 'unauthAccess')

@app.route('/stats/<video_id>', methods=['GET', 'POST'])
def perform_stats(video_id):
    if "username" not in session:
        return "Unauthorized Access"
    attr = request.args.get('attr')
    action = request.args.get('action')
    if not attr or not action:
        return "Invalid Request"
    if attr == "like" or attr == "dislike" or attr=="favourite":
        success = False
        if action == "0":
            success = decrement(session['username'],video_id,attr,graph)
        elif action == "1":
            success = increment(session['username'],video_id,attr,graph)
        else:
            return "Invalid Request"
        if success:
            return "Success"
        else:
            return "Failed"
    else:
        return "Invalid Request"

@app.route('/update_history', methods=['GET', 'POST'])
def update_history():
    q = request.args.get('q')
    v = request.args.get('v')
    p = request.args.get('p')
    url_param = "?"
    url_param = (url_param + "q="+q+"&&") if q else url_param
    url_param = (url_param + "v="+v+"&&") if v else url_param
    url_param = (url_param + "p="+p+"&&") if p else url_param
    if q or p or v:
        url_param = url_param[:-2]
    else:
        url_param = ""
    if 'username' in session and v:
        if request.method == 'GET':
            q = request.args.get('q')
            v = request.args.get('v')
            p = request.args.get('p')

            sql = "INSERT INTO history(s_no,username,video_id,viewed_at) VALUES (default,'%s', '%s',default)" %(session['username'],v) 
            try:
                    cursor.execute(sql)
                    db.commit()
            except:
                    db.rollback()

            return redirect("/"+url_param)
    return redirect("/"+url_param)

@app.route('/addComment',methods=['GET','POST'])
def comment():
    if 'username' in session:
        if request.method == 'POST':
            comment = request.form['comment']
            v = request.form['v']
            if not comment or not v:
                return "Invalid Request"
            sql = "INSERT into video_comment(s_no,username,video_id,comment_given,commented_at) VALUES (default,'%s','%s','%s',default)" % (session['username'],v,comment)
 
            try:
                cursor.execute(sql)
                db.commit()
                return "Success"
            except:
                db.rollback()
                return "Failed"
        else:
            return "Invalid Request"
 
        
    return "Unauthorised Access"

@app.route('/history')
def history():
    if 'username' in session:
        sql = "SELECT video_id from history Where username='%s'" %(session['username']) 
        # try:
        cursor.execute(sql)
        db.commit()
        result=cursor.fetchall()
        video_ids = [a[0] for a in result]
        videos = get_videos_from_list(video_ids)


        return render_template('history.html',results = videos)
        # except:
        #     return redirect(url_for("index"))

    return redirect(url_for("login"))

@app.route('/playlist', methods=['GET'])
def playlist():
    if 'username' not in session:
        return redirect(url_for("login"))

    if request.method == 'GET':
        pid = request.args.get('pid')
        p=request.args.get('p')
        if not p:
            p=0

        if not pid :
            username = session['username']
            user = {'username':username}
            user_playlist = get_owned_playlists(graph,user)
            liked_playlist = get_liked_playlists(graph, user)
            return render_template('playlist.html',user_playlist = user_playlist, liked_playlist = liked_playlist)
        else :
            playlist={}
            playlist["id"]=pid
            user={"username":session["username"]}
            like=is_like_playlist(graph,user,playlist)
            playlist=get_playlist_details(graph,pid)
            vid_id_list=get_videos_in_playlist(graph,playlist,p*10,10)
            vid_list_details=get_videos_from_list(vid_id_list)
            return render_template('playlist_page.html',q_results=vid_list_details,like=int(like),playlist_details=playlist)


@app.route('/playlist/<playlist_id>', methods=['POST','GET'])           
def like_dislike_playlist(playlist_id):
    if "username" not in session:
        return "Unauthorized Access"

    
    # return "reached"
    user={"username":session["username"]}
    playlist={"id":playlist_id}
    if (is_like_playlist(graph,user,playlist)):
        unlike_playlist(graph,user,playlist)
    else:
        like_playlist(graph,user,playlist)
    return "Success"        


@app.route('/mostViewed')
def mostViewedVideos():
    videos = getVideos("viewCount",20)
    return render_template('mostViewedVideos.html', videos = videos)

@app.route('/mostLiked')
def mostLikedVideos():
    videos = getVideos("likeCount",20)
    return render_template('mostLikedVideos.html', videos = videos)

@app.route('/test_login')
def test_login():
    session['username'] = "sample_user"
    return "You have logged in"

@app.route('/logout')
def test_logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/login_status')
def login_status():
    if 'username' in session:
        username = session['username']
        return "Logged in as " + username
    return "You are not logged in."

@app.route('/test_page')
def test_page():
    return "test success"

@app.route('/fetchComments', methods=['GET', 'POST'])
def fetchcomment():
    if request.method == 'POST':
        v = request.form['v']
        sql = "SELECT username,comment_given from video_comment Where video_id='%s' order by commented_at DESC" %(v)
        # try:
        cursor.execute(sql)
        db.commit()
        output = ""
        for res in cursor.fetchall():
            output+="<div class='panel panel-default'><div class='panel-body'><b>"+res[0]+"</b><br>"+res[1]+"</div></div>"+"\n"
        return output
        # except:
        #         db.rollback()
        #         return "Error Loading Comments1"

        
    return "Error Loading Comments2"


@app.route('/create_playlist',methods=['POST'])

def create_playlist_form():
    print("Are we here")
    if 'username' in session:
        if request.method == 'POST':
            playlist_name  = request.form['name']
            playlist_description  = request.form['description']
            playlist={}
            playlist["name"]=playlist_name
            playlist["description"]=playlist_description
            user={}
            user["username"]=session["username"]
            print(user,playlist)
            pid=create_playlist(graph,user,playlist)
            return redirect('/playlist?pid='+pid)



@app.route('/createPlaylist.html')
def serve_create_playlist_form():
    if 'username' in session:
        return render_template('createPlaylist.html')
    else:
        print("Unauthorized Access")


@app.route('/addToPlaylist',methods=["GET"])
def addToPlaylist():
    if 'username' not in session:
        return 'Unauth Acess'
    playlist_id = request.args.get('pid')
    video_id = request.args.get('v')
    playlist={"id":playlist_id}
    # return str(playlist)
    video={"videoId":video_id}
    success = add_video_playlist(graph,playlist,video)
    if success:
        return "True"
    else:
        return "Failed"




if __name__ == '__main__':
    app.run(debug = True)