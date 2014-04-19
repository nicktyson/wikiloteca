# Nicholas Tyson
# March 2014

import boto.sqs
from boto.sqs.message import Message
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from boto.dynamodb2.table import Table

import lxml.etree
import lxml.html

import json
from collections import deque
import datetime

##########################################################################
# Functions
##########################################################################

#add a new unprocessed article title to the database and queue
#check that the title hasn't been added already BEFORE calling this
#========================================
def add_new_title(title):
	add_time = str(datetime.datetime.now())
	database.put_item(data={
		'title': title,
		'status': 'queued',
		'difficulty': 0,
		'time': add_time,
	})
	message = Message()
	message.set_body(title.encode('utf-8'))
	q.write(message)


#set the language and initial list of article titles
#===============================
def init(language, seed_list):
	print "initializing"
	for seed in seed_list:
		add_new_title(seed)

	global URL_ROOT
	global LINKS_ROOT

	if language == "english":
		URL_ROOT += "http://en.wikipedia.org/wiki/"
		LINKS_ROOT += "http://en.wikipedia.org/w/api.php?action=parse&format=xml&prop=links&page="
	elif language == "spanish":
		URL_ROOT = "http://es.wikipedia.org/wiki/"
		LINKS_ROOT= "http://es.wikipedia.org/w/api.php?action=parse&format=xml&prop=links&page="
	else:
		URL_ROOT = "http://en.wikipedia.org/wiki/"
		LINKS_ROOT= "http://en.wikipedia.org/w/api.php?action=parse&format=xml&prop=links&page="


#open AWS connections
#=====================================
def initAWS():
	print "initializing AWS"


#returns the next article that should be processed
#======================================
def choose_article():
	message = q.read()
	if message is not None:
		print "choosing article: " + message.get_body()
		return (message.get_body()).decode('utf-8')
	else:
		print "No message"
		return "Boat"


#get the data from online and prepare it for later processing
#adds new links to the queue
#returns the article's text
#=======================================
def process_article(article_title):
	print "processing " + article_title

	html_tree = lxml.html.parse(URL_ROOT + article_title)
	paragraph_tags = html_tree.xpath("//p")
	paragraphs = [p.text_content() for p in paragraph_tags]

	content = ""
	for p in paragraphs:
		content += (p + "\n\n")

	return content


#download the list of links in the article and add them to the queue
#============================================
def process_links(article_title):
	print "processing links for " + article_title
	links_tree = lxml.etree.parse(LINKS_ROOT + article_title)
	link_nodes = links_tree.xpath("//pl[@ns='0' and @exists='']")
	links = [l.text for l in link_nodes]

	#add links to the queue if they haven't been seen before
	request_list = []
	for t in links:
		request_list = request_list + [dict(title=t)]
	
	#returns list of dicts - each dict is one item from the database
	present_links = database.batch_get(keys=request_list)
	
	with database.batch_write() as batch:
		for r in request_list:
			#find titles in the returned list that match requested titles
			# if none exist, add the item to the database and queue
			matches = [item for item in present_links if item['title'] == r['title']]
			if len(matches) == 0:
				add_time = str(datetime.datetime.now())
				batch.put_item(data={
					'title': r['title'],
					'status': 'queued',
					'difficulty': 0,
					'time': add_time,
				})
				message = Message()
				message.set_body(r['title'].encode('utf-8'))
				q.write(message)
				print "adding article to queue: " + r['title']
			

#determine text difficulty
#======================================
def determine_difficulty(text):
	print "determining difficulty"
	return 0


#add the article's difficulty to the database and mark it as done
#===========================================
def update_processed_article_in_database(article_title, difficulty):
	#mark the article as processed
	article_data = database.get_item(title=article_title, consistent=True)
	article_data['status'] = 'done'
	article_data['difficulty'] = difficulty
	article_data.save()


#save an article to a local file for eventual upload to S3
#======================================
def update_archive(article_title, content):
	archive[article_title] = content


#upload the article texts to S3
#======================================
def upload_archive():
	print "uploading to S3"
	archive_string = json.dumps(archive)
	k = Key(bucket)
	k.key = str(datetime.datetime.now())
	k.set_contents_from_string(archive_string)
	archive.clear()


#close AWS connections and stuff
#======================================
def closeAWS():
	print "closing AWS connections"


############################################################################
# Script
############################################################################

#global variables and constants
seed_list = ["Boat"]
URL_ROOT = ""
LINKS_ROOT = ""

archive = dict()
last_archive_time = datetime.datetime.now()

sqs = boto.sqs.connect_to_region("us-east-1")
#returns the existing queue if one exists already
q = sqs.create_queue("wikiloteca_queue")

s3 = S3Connection()
bucket = s3.get_bucket("nickgtyson.wikiloteca")

# title -> status, difficulty, time
database = Table("wikiloteca")


init("english", seed_list)

articles_processed = 0
while (articles_processed < 3):
	article = choose_article()
	words = process_article(article)
	process_links(article)
	difficulty = determine_difficulty(words)
	update_processed_article_in_database(article, difficulty)
	update_archive(article, words)	
	articles_processed += 1
	
	#see if it has been long enough to backup data to S3
	current_time = datetime.datetime.now()
	time_since_backup = current_time - last_archive_time
	if (time_since_backup.seconds >= 1800):
		upload_archive()
		last_archive_time = current_time
	
