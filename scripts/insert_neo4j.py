from py2neo import Graph, Node, Relationship
import json
import os
import sys
from bson import ObjectId
import pickle



#add videos to graph
#add channels to graph
#add category ids
#add tag relation to graph
#add description relation to graph
def first_insert(graph,data_array):
	print("Inserting Video, Channel, Category nodes & creating relations BelongsToChannel,HasCategory")
	channel_dict={}
	category_dict={}
	video_node_dict={}
	i=0
	for video_dict in data_array:
		video_stats = video_dict['videoInfo']['statistics']
		video_id=video_dict['videoInfo']['id']
		video_node = Node ("Video", title=video_dict['videoInfo']['snippet']['title'],videoId = video_id,commentCount=int(video_stats['commentCount']),viewCount=int(video_stats['viewCount']),favoriteCount=int(video_stats['favoriteCount']),dislikeCount=int(video_stats['dislikeCount']),likeCount=int(video_stats['likeCount']))
		video_node_dict[video_id]=video_node
		graph.create(video_node)

		channelId=video_dict['videoInfo']['snippet']['channelId']
		channelTitle=video_dict['videoInfo']['snippet']['channelTitle']
		categoryId=video_dict['videoInfo']['snippet']['categoryId']
		channel_node=None
		if channelId not in channel_dict:
			channel_node=Node("Channel",channelId=channelId,channelTitle=channelTitle)
			channel_dict[channelId]=channel_node
			graph.create(channel_node)
		else:
			channel_node=channel_dict[channelId]

		channel_relation=Relationship(video_node,"BelongsToChannel",channel_node)
		graph.create(channel_relation)

		category_node=None
		if categoryId not in category_dict:
			category_node=Node("Category",categoryId=categoryId,categoryTitle="Category"+categoryId)
			category_dict[categoryId]=category_node
			graph.create(category_node)
		else:
			category_node=category_dict[categoryId]
		category_relation=Relationship(video_node,"HasCategory",category_node)
		graph.create(category_relation)
		i+=1
		print("Done processing "+str(i))


	print(channel_dict)
	print(category_dict)


def test_insert(graph):
	graph.create( Node ("Video", title="testvideo",videoId = "1234",commentCount=0,viewCount=0,favoriteCount=0,dislikeCount=0,likeCount=0))
	graph.create(Node("Channel",channelId="h2312",channelTitle="testchannel"))
	graph.create(Node("Category",categoryId="343",categoryTitle="testcategory"))
	graph.create(Node("User",username="testuser",sex="M"))
	graph.create(Node("Playlist",id="dfsdF12",name="testplaylist",description="description",createdOn=123134, lastModified=124144,no_videos=0,likes=0))

def create_indexes(graph):
	graph.run("CREATE INDEX ON :Video(videoId)")
	graph.run("CREATE INDEX ON :Channel(channelId)")
	graph.run("CREATE INDEX ON :Category(categoryId)")
	graph.run("CREATE INDEX ON :User(username)")
	graph.run("CREATE INDEX ON :Playlist(id)")

def descriptionCompare(description1,description2,stop_words):
	word_description1 = description1.split()
	word_description2 = description2.split()
	count = len((set(word_description2)&set(word_description1))-stop_words)
	return count

def tagsCompare(tags1,tags2):
	return len(set(tags1)&set(tags2))

def load_stop_words():
	s=set()
	with open("../stop_words.txt","r") as f:
		for line in f:
			s.add(line.strip())
	print(s)
	return s


def second_insert(graph,data_array,stop_words):
	match_desc_count=0
	match_tags_count=0
	match_title_count=0
	for i in range(len(data_array)):
		element = data_array[i]
		for j in range(i-1,-1,-1):
			count=descriptionCompare(data_array[i]['videoInfo']['snippet']['description'],data_array[j]['videoInfo']['snippet']['description'],stop_words)
			if count >10:
				a = graph.find_one("Video",property_key='videoId', property_value=element['videoInfo']['id'])
				b = graph.find_one("Video",property_key='videoId', property_value=data_array[j]['videoInfo']['id'])
				DescriptionRelation = Relationship(a,"SimilarDescription",b,weightage=count)
				graph.create(DescriptionRelation)
				print("New SimilarDescription found")
				match_desc_count+=1

			count=descriptionCompare(data_array[i]['videoInfo']['snippet']['title'],data_array[j]['videoInfo']['snippet']['title'],stop_words)
			
			if count >0:
				a = graph.find_one("Video",property_key='videoId', property_value=element['videoInfo']['id'])
				b = graph.find_one("Video",property_key='videoId', property_value=data_array[j]['videoInfo']['id'])
				DescriptionRelation = Relationship(a,"SimilarTitle",b,weightage=count)
				graph.create(DescriptionRelation)
				print("New SimilarTitle found")
				match_title_count+=1


			if 'tags' in data_array[i]['videoInfo']['snippet'] and 'tags' in data_array[j]['videoInfo']['snippet']:
				tagCount = tagsCompare(data_array[i]['videoInfo']['snippet']['tags'], data_array[j]['videoInfo']['snippet']['tags'])
				if tagCount >3:
					a = graph.find_one("Video",property_key='videoId', property_value=element['videoInfo']['id'])
					b = graph.find_one("Video",property_key='videoId', property_value=data_array[j]['videoInfo']['id'])
					TagRelation = Relationship(a,"MatchingTags",b,weightage=tagCount)
					graph.create(TagRelation)
					print("New MatchingTags found")
					match_tags_count+=1
		print("Finished processing "+str(i))

	print("Total "+str(match_desc_count)+ " SimilarDescription found")
	print("Total "+str(match_title_count)+ " SimilarTitle found")
	print("Total "+str(match_tags_count)+ " MatchingTags found")

def load_jsons(data_path,toomuch):
	stopper=0
	print("Loading JSON files...")
	data_array=[]
	for file_name in os.listdir(data_path):
		stopper+=1
		if (stopper >toomuch):
			break

		file_name=data_path+file_name
		print("Processing "+file_name+"...")
		with open(file_name,"r") as json_file :
			video_dict = json.loads(json_file.read())
			data_array.append(video_dict)
	return data_array


data_path="./../data/"
home="./../"
option = sys.argv[1]
print("Your option is "+str(option))



graph = Graph(host="localhost",port=7474,password='pra')


if int(option)==1:
	data_array=load_jsons(data_path,int(sys.argv[2]))
	first_insert(graph,data_array)
if int(option)==2:
	data_array=load_jsons(data_path,int(sys.argv[2]))
	second_insert(graph,data_array,load_stop_words())
if int(option)==3:
	test_insert(graph)
if int(option)==4:
	create_indexes(graph)
if option==5:
	graph.delete_all()













