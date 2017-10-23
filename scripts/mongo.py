import pymongo
from pymongo import MongoClient
import os
import json

client = MongoClient('mongodb://admin:' + 'prateek' + '@127.0.0.1')
db = client['lab_db']
collection = client['youtube']

for f in os.listdir("test/"):
	file = open("test/"+f, 'r')
	document = file.read()
	js = json.loads(document)
	js['videoInfo']['statistics']['likeCount'] = int(js['videoInfo']['statistics']['likeCount'])
	result = db.youtube.insert_one(js)
	print result