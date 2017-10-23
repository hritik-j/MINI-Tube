import pymongo
from pymongo import MongoClient, TEXT

client = MongoClient('mongodb://localhost:27017/')
db = client['video_db']
collection = db['video_collection']

q = "currency"
raw_results = db.video.find({"$text": {"$search": q}},{'weights': {'$meta': 'textScore'}})
results = raw_results.sort([('weights', {'$meta': 'textScore'})])

# for doc in raw_results.limit(10):
# 	print doc['videoInfo']['snippet']['title']
print results.limit(5).fetchall()
