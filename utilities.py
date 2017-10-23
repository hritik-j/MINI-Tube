import pymongo
from pymongo import MongoClient, TEXT
from bson import BSON
from bson import json_util
import json
from recommend import related_videos
from py2neo import Graph
from graph_utils import *

client = MongoClient('mongodb://localhost:27017/')
db = client['video_db']

#video_db->video_collection
def q_search(q,p):
	raw_results = db.video.find({"$text": {"$search": q}},{'weights': {'$meta': 'textScore'}})
	iterator = raw_results.sort([('weights', {'$meta': 'textScore'})]).skip(p*10).limit(10)
	return iterator

def increment(username,video_id,stat, graph):
	statistics = {"like":"likeCount", "dislike": "dislikeCount","favourite":"favoriteCount" }
	user = {'username':username}
	video = {'videoId':video_id}
	if stat == "like":
		if is_dislike_video(graph,user,video):
			db.video.find_and_modify(query = {"videoInfo.id":video_id}, update = {"$inc": {"videoInfo.statistics."+'dislikeCount':-1} })

		if is_like_video(graph,user,video):
			return False
		else:
			like_video(graph,user,video)
			db.video.find_and_modify(query = {"videoInfo.id":video_id}, update = {"$inc": {"videoInfo.statistics."+statistics[stat]:1} })
			return True
	if stat == "dislike":
		if is_like_video(graph,user,video):
			db.video.find_and_modify(query = {"videoInfo.id":video_id}, update = {"$inc": {"videoInfo.statistics."+'likeCount':-1} })

		if is_dislike_video(graph,user,video):
			return False
		else:
			dislike_video(graph,user,video)
			db.video.find_and_modify(query = {"videoInfo.id":video_id}, update = {"$inc": {"videoInfo.statistics."+statistics[stat]:1} })
			return True	
	return False;

def decrement(username,video_id,stat, graph):
	statistics = {"like":"likeCount", "dislike": "dislikeCount","favourite":"favoriteCount" }
	user = {'username':username}
	video = {'videoId':video_id}
	if stat == "like":
		if not is_like_video(graph,user,video):
			return False
		else:
			unlike_video(graph,user,video)
			db.video.find_and_modify(query = {"videoInfo.id":video_id}, update = {"$inc": {"videoInfo.statistics."+statistics[stat]:-1} })
			return True
	if stat == "dislike":
		if not is_dislike_video(graph,user,video):
			return False
		else:
			undislike_video(graph,user,video)
			db.video.find_and_modify(query = {"videoInfo.id":video_id}, update = {"$inc": {"videoInfo.statistics."+statistics[stat]:-1} })
			return True	
	return False;

def get_details(video_id):
	cursor = db.video.find_one({"videoInfo.id":video_id})
	return cursor

def getVideos(stat, num):
	param = "videoInfo.statistics."+stat
	cursor = db.video.find({}).sort(param,-1).limit(num)
	return cursor

def get_videos_from_list(vlist):
	vlist_details=[]
	for v_id in vlist:
		vlist_details.append(get_details(v_id))
	return vlist_details


# graph = Graph(host="localhost",port=7474,password="pra")
#NSG Lieutenant Colonel Among 7 Martyred in Pathankot Terror Attack
# video={"videoId":"3hovOXcrZSQ"}
# vlist=related_videos(graph,video,10)
# print(vlist)
# print(db.video.find_one({"videoInfo.id":"3hovOXcrZSQ"}))
# print(get_videos_from_list(vlist))
# 