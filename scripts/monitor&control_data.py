import pymongo
from pymongo import MongoClient, TEXT
import pprint

client = MongoClient('mongodb://localhost:27017/')
db = client['video_db']

# db.video.find_and_modify(query = {"videoInfo.id":"0rLSBy57xx0"}, update = {"$inc": {"videoInfo.statistics.likeCount":-1} })
pprint.pprint((db.video.find_one({"videoInfo.id":"0rLSBy57xx0"}))['videoInfo']['statistics'])
