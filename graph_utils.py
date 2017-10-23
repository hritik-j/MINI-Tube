from py2neo import Graph, Node, Relationship
from datetime import datetime
import time
import hashlib
#create user function 
#create playlist function
#add video to playlist function
#get n results from playlist, starting at k
#get playlists for video
#add like relation
#add dislike relation
#subscribe to channel
#islike?
#is dislike?

#okay
def create_user(graph,user):
	graph.create(Node("User",username=user["username"],sex=user["sex"]))#,age=user["age"]))

#okay
def delete_user(graph,user):
	query_string="MATCH (u:User) WHERE u.username = \""+user["username"]+"\" detach delete u"
	graph.run(query_string)

#playlist exists purely in neo4j
#send sanitized inputs
#okay
def create_playlist(graph,user,playlist):
	now = datetime.now()
	createdOn=time.mktime(now.timetuple())
	pid =str(hashlib.sha224(str(createdOn)).hexdigest())
	playlist_node=Node("Playlist",id=pid,name=playlist["name"],description=playlist["description"],createdOn=createdOn, lastModified=createdOn,no_videos=0,likes=0)
	graph.create(playlist_node)
	username=user["username"]
	user_node=graph.find_one("User","username",username)
	ownership_relation=Relationship(user_node,"OwnsPlaylist",playlist_node)
	graph.create(ownership_relation)
	return pid

#okay
def delete_playlist(graph,playlist):
	query_string="MATCH (p:Playlist) WHERE p.id = \""+playlist["id"]+"\" detach delete p"
	graph.run(query_string)


#check already exists?
#okay
def add_video_playlist(graph,playlist,video):
	now = datetime.now()
	lastModified=time.mktime(now.timetuple())

	query_string="MATCH (v:Video)-[:InPlaylist]->(p:Playlist) WHERE v.videoId=\""+video["videoId"]+"\" AND p.id=\""+playlist["id"]+"\" RETURN p.id LIMIT 1"
	print(query_string)
	cursor=graph.run(query_string)
	# cursor.dump()
	# print(cursor.forward())
	# return
	if cursor.forward(): #true=nonempty result=alreadyexists
		print("Video already exists in playlist")
		return False

	# query_string="MATCH (p:PLAYLIST) WHERE p.id="+playlist["id"]+" SET p.no_videos = p.no_videos + 1"
	video_node=graph.find_one("Video","videoId",video["videoId"])
	playlist_node=graph.find_one("Playlist","id",playlist["id"])
	playlist_node["no_videos"]=playlist_node["no_videos"]+1
	if playlist_node["no_videos"]==1:
		playlist_node["first"]=video_node["videoId"]
	playlist_node["lastModified"]=lastModified
	playlist_node.push()
	playlist_relation=Relationship(video_node,"InPlaylist",playlist_node)
	playlist_relation["pos"]=playlist_node["no_videos"]
	graph.create(playlist_relation)
	return True

#okay
def get_owned_playlists(graph,user):
	query_string="MATCH (u:User)-[:OwnsPlaylist]->(p:Playlist) WHERE u.username=\""+user["username"]+"\" RETURN p.id,p.name,p.description"
	cursor=graph.run(query_string)
	playlists=[]
	for record in cursor:
		playlist={}
		playlist["id"]=record["p.id"]
		playlist["name"]=record["p.name"]
		playlist["description"]=record["p.description"]
		playlists.append(playlist)
	return playlists

#okay
def get_liked_playlists(graph,user):
	query_string="MATCH (u:User)-[:LikesPlaylist]->(p:Playlist) WHERE u.username=\""+user["username"]+"\" RETURN p.id,p.name,p.description"
	cursor=graph.run(query_string)
	playlists=[]
	for record in cursor:
		playlist={}
		playlist["id"]=record["p.id"]
		playlist["name"]=record["p.name"]
		playlists.append(playlist)
	return playlists

#okay
def get_playlist_details(graph,playlist_id):
	query_string="MATCH (p:Playlist) WHERE p.id=\""+playlist_id+"\" RETURN p.id,p.name,p.description,p.lastModified,p.createdOn LIMIT 1 "
	record=graph.run(query_string).data()[0]
	playlist={}
	playlist["id"]=record["p.id"]
	playlist["name"]=record["p.name"]
	playlist["description"]=record["p.description"]
	playlist["createdOn"]=record["p.createdOn"]
	playlist["lastModified"]=record["p.lastModified"]
	return playlist


#okay
def get_playlists_containing_video(graph,video):
	query_string="MATCH (v:Video)-[:InPlaylist]->(p:Playlist) WHERE v.videoId=\""+video["videoId"]+"\" RETURN p.id ,p.name,p.first"
	cursor=graph.run(query_string)
	playlists=[]
	for record in cursor:
		playlist={}
		playlist["id"]=record["p.id"]
		playlist["first"]=record["p.first"]
		playlist["name"]=record["p.name"]
		playlists.append(playlist)
	return playlists



#add to liked videos
#okay
#increase likes of video?
def like_video(graph,user,video):
	if (is_dislike_video(graph,user,video)):
		undislike_video(graph,user,video)
	query_string="MATCH (u:User),(v:Video) WHERE u.username = \""+user["username"]+"\" AND v.videoId =\""+video["videoId"]+"\" CREATE (u)-[r:LikesVideo]->(v) "
	graph.run(query_string)

#okay
def unlike_video(graph,user,video):
	query_string="MATCH (u:User)-[r:LikesVideo]->(v:Video) WHERE u.username = \""+user["username"]+"\" AND v.videoId =\""+video["videoId"]+"\" delete r"
	graph.run(query_string)

#okay
def is_like_video(graph,user,video):
	query_string="MATCH (u:User)-[r:LikesVideo]->(v:Video) WHERE v.videoId=\""+video["videoId"]+"\"AND u.username=\""+user["username"]+"\" RETURN r LIMIT 1"
	if graph.run(query_string).forward():
		return True
	else :
		return False
#okay
def dislike_video(graph,user,video):
	if (is_like_video(graph,user,video)):
		unlike_video(graph,user,video)
	query_string="MATCH (u:User),(v:Video) WHERE u.username = \""+user["username"]+"\" AND v.videoId =\""+video["videoId"]+"\" CREATE (u)-[r:DislikesVideo]->(v) "
	graph.run(query_string)

#okay
def undislike_video(graph,user,video):
	query_string="MATCH (u:User)-[r:DislikesVideo]->(v:Video) WHERE u.username = \""+user["username"]+"\" AND v.videoId =\""+video["videoId"]+"\" delete r"
	graph.run(query_string)

#okay
def is_dislike_video(graph,user,video):
	query_string="MATCH (u:User)-[r:DislikesVideo]->(v:Video) WHERE v.videoId=\""+video["videoId"]+"\"AND u.username=\""+user["username"]+"\" RETURN r LIMIT 1"
	if graph.run(query_string).forward():
		return True
	else :
		return False


#WARNING Don't have like button for own playlist
#okay
def like_playlist(graph,user,playlist):
	query_string="MATCH (u:User),(p:Playlist) WHERE u.username = \""+user["username"]+"\" AND p.id =\""+playlist["id"]+"\" CREATE (u)-[r:LikesPlaylist]->(p) "
	graph.run(query_string)
	query_string="MATCH (p:Playlist) WHERE p.id=\""+playlist["id"]+"\" SET p.likes=p.likes+1"
	graph.run(query_string)


#okay
def unlike_playlist(graph,user,playlist):
	query_string="MATCH (u:User)-[r:LikesPlaylist]->(p:Playlist) WHERE u.username = \""+user["username"]+"\" AND p.id =\""+playlist["id"]+"\" delete r"
	graph.run(query_string)
	query_string="MATCH (p:Playlist) WHERE p.id=\""+playlist["id"]+"\" SET p.likes=p.likes-1"
	graph.run(query_string)

#okay
def is_like_playlist(graph,user,playlist):
	query_string="MATCH (u:User)-[r:LikesPlaylist]->(p:Playlist) WHERE p.id =\""+playlist["id"]+"\"AND u.username=\""+user["username"]+"\" RETURN r LIMIT 1"
	if graph.run(query_string).forward():
		return True
	else :
		return False

def get_videos_in_channel(graph,channel_id,skip,number):
	query_string="MATCH (v:Video)-[r:BelongsToChannel]->(c:Channel) WHERE c.channelId=\""+channel_id+"\" RETURN v.videoId ORDER BY v.videoId SKIP "+str(skip)+" LIMIT "+str(number)
	cursor=graph.run(query_string)
	# cursor.dump()
	# return
	videos=[]
	for record in cursor:
		videos.append(record["v.videoId"])
	return videos

def get_videos_in_playlist(graph,playlist,skip,number):
	query_string="MATCH (v:Video)-[r:InPlaylist]->(p:Playlist) WHERE p.id=\""+playlist["id"]+"\" RETURN v.videoId ORDER BY r.pos SKIP "+str(skip)+" LIMIT "+str(number)
	cursor=graph.run(query_string)
	# cursor.dump()
	# return
	videos=[]
	for record in cursor:
		videos.append(record["v.videoId"])
	return videos




# def addFavourite(user,video):
# 	query_string="MATCH (u:User),(v:Video) WHERE u.username = "+user["username"]+" AND v.videoId = "+video["videoId"]+" CREATE (u)-[r:Favourites]->(v) "
# 	graph.cypher.execute(query_string)

# def isFavourite(user,video):
# 	query_string="MATCH (u:User)-[:Favourites]->(v:Video) WHERE v.videoId="+video["videoId"]+"AND u.username="+user["username"]+" RETURN p.id LIMIT 1"
# 	if graph.cypher.execute(query_string):
# 		return True
# 	else :
# 		return False




# graph = Graph(host="localhost",port=7474,password='civilwargnr')

# user={"username":"shashank_chutiya","sex":"F"}
# user={"username":"hritik_chutiya","sex":"F"}
# # playlist={"id":"1" ,"name":"chutiyapa","description":"i am chutiya"}
# playlist={"id":"6" ,"name":"mai chutiya shash6","description":"i am chutiya"}
# # playlist={"id":"4" ,"name":"mai chutiya shash part 2","description":"i am chutiya"}


# # video={"videoId":"_lWzjh3QYlM"} #in 3 playlists
# # video={"videoId":"7khMaljrte0"}
# video={"videoId":"7ME9SF6rO10"}

# create_user(graph,user)
# print(create_playlist(graph,user,playlist))
# delete_playlist(graph,playlist)
# add_video_playlist(graph,playlist,video)
# delete_user(graph,user)
# print(get_owned_playlists(graph,user))
# print(get_playlist_details(graph,"4"))
# print(get_playlists_containing_video(graph,video))
# like_video(graph,user,video)
# unlike_video(graph,user,video)
# dislike_video(graph,user,video)
# undislike_video(graph,user,video)
# print(is_like_video(graph,user,video))
# print(is_dislike_video(graph,user,video))
# like_playlist(graph,user,playlist)
# unlike_playlist(graph,user,playlist)
# print(is_like_playlist(graph,user,playlist))
# print(get_liked_playlists(graph,user))
# print(get_videos_in_playlist(graph,playlist,0,10))
# print(get_videos_in_channel(graph,"UCZFMm1mMw0F81Z37aaEzTUA",5,5))




















