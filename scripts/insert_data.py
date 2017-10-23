import pymongo
from pymongo import MongoClient, TEXT
import os
import json

client = MongoClient('mongodb://localhost:27017/')
db = client['video_db']
mongo_dict={}
home="./../"
#video_db->video_collection
for f in os.listdir("./../data/"):
	filename = "./../data/"+f
	file = open(filename, 'r')
	document = file.read()
	js = json.loads(document)
	js['videoInfo']['statistics']['likeCount'] = int(js['videoInfo']['statistics']['likeCount'])
	result = db.video_collection.insert_one(js)
	mongo_dict[js['videoInfo']['id']]=str(result.inserted_id)
	print(result)
print("Done inserting data. Indexing them now")

with open(home+"mongo_dict.json","w") as json_f:
	json.dump(mongo_dict,json_f)

result = db.video_collection.create_index([('videoInfo.snippet.tags',TEXT),('videoInfo.snippet.title',TEXT),('videoInfo.snippet.description',TEXT) ],weights = { 'videoInfo.snippet.tags': 5, 'videoInfo.snippet.title': 5,'videoInfo.snippet.description':1 }, name = "video_index",default_language='english' )
print(result)