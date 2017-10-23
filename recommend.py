from py2neo import Graph
import operator
#similar desc max = 60, avg=20
#match tags max =20 , avg =10
def related_videos(graph,video,n):

	videoId=video["videoId"]
	avg_weightage = 5
	avg_weightage2 = 5
	query_string="MATCH (v1:Video)-[r:SimilarDescription]-(v2:Video) WHERE v1.videoId=\""+videoId+"\" RETURN v2.videoId , r.weightage , avg(r.weightage),v2.title  ORDER BY r.weightage"
	records=graph.run(query_string).data()
	if (len(records)>0):
		avg_weightage=int(records[0]["r.weightage"])
		print(avg_weightage)
	scoremap={}
	titlemap={}
	for record in records:
		# if (record["r.weightage"] < avg_weightage): #skip averagely related videos
		# 	pass
		scoremap[record["v2.videoId"]]=int(record["r.weightage"])
		titlemap[record["v2.videoId"]]=record["v2.title"]


	query_string="MATCH (v1:Video)-[r:SimilarTitle]-(v2:Video) WHERE v1.videoId=\""+videoId+"\" RETURN v2.videoId , r.weightage , avg(r.weightage),v2.title  ORDER BY r.weightage"
	records=graph.run(query_string).data()
	scoremap={}
	titlemap={}
	for record in records:
		# if (record["r.weightage"] < avg_weightage): #skip averagely related videos
		# 	pass
		if record["v2.videoId"] not in scoremap:
			scoremap[record["v2.videoId"]]=5*int(record["r.weightage"])
			titlemap[record["v2.videoId"]]=record["v2.title"]
		else:
			scoremap[record["v2.videoId"]]+=5*int(record["r.weightage"])
	
	query_string="MATCH (v1:Video)-[r:MatchingTags]-(v2:Video) WHERE v1.videoId=\""+videoId+"\" RETURN v2.videoId , r.weightage , avg(r.weightage),v2.title   ORDER BY r.weightage"
	records=graph.run(query_string).data()
	if (len(records)>0):
		avg_weightage2=int(records[0]["r.weightage"])
		print(avg_weightage2)
	for record in records:
		# if (record["r.weightage"] < avg_weightage): #skip averagely related videos
		# 	pass
		if record["v2.videoId"] not in scoremap:
			scoremap[record["v2.videoId"]]=2*int(record["r.weightage"])
			titlemap[record["v2.videoId"]]=record["v2.title"]
		else:
			scoremap[record["v2.videoId"]]+=2*int(record["r.weightage"])

	
	query_string="MATCH (v1:Video)-[:BelongsToChannel]-(:Channel)-[:BelongsToChannel]-(v2:Video) WHERE v1.videoId=\""+videoId+"\" RETURN v2.videoId,v2.title  "
	records=graph.run(query_string).data()
	for record in records:
		if record["v2.videoId"] not in scoremap:
			scoremap[record["v2.videoId"]]=avg_weightage/2
			titlemap[record["v2.videoId"]]=record["v2.title"]
		else:
			scoremap[record["v2.videoId"]]+=avg_weightage/2

	
	query_string="MATCH (v1:Video)-[:HasCategory]-(:Category)-[:HasCategory]-(v2:Video) WHERE v1.videoId=\""+videoId+"\" RETURN v2.videoId,v2.title  ORDER BY v2.viewCount DESC LIMIT 10"
	records=graph.run(query_string).data()
	for record in records:
		if record["v2.videoId"] not in scoremap:
			scoremap[record["v2.videoId"]]=avg_weightage/4
			titlemap[record["v2.videoId"]]=record["v2.title"]
		else:
			scoremap[record["v2.videoId"]]+=avg_weightage/4

	i=0
	video_list=[]
	score_list=[]
	print(len(scoremap))
	sorted_scoremap = sorted(scoremap.items(), key=operator.itemgetter(1),reverse=True)
	# print(sorted_scoremap)
	for i in range(0,n):
		video_list.append(sorted_scoremap[i][0])
		score_list.append(sorted_scoremap[i][1])

	# return video_list,titlemap,score_list
	return video_list


# graph = Graph(host="localhost",port=7474,password="civilwargnr")
#Congress Workers Protest over Note Ban in Ahmedabad
# video={"videoId":"aduoP0NEDRE"}
#NSG Lieutenant Colonel Among 7 Martyred in Pathankot Terror Attack
# video={"videoId":"3hovOXcrZSQ"}

# (vlist,tmap,slist)=related_videos(graph,video,10)
# for i in range(0,10):
# 	print(vlist[i],slist[i], tmap[vlist[i]])

	




