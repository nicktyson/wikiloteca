# Nicholas Tyson
# March 2014

import lxml.etree
import lxml.html
from collections import deque
import datetime

##########################################################################
# Functions
##########################################################################

#set the language and initial list of article titles
#===============================
def init(language, seed_list):
	#eventually put them in SQS instead
	for seed in seed_list:
		status[seed] = 0
		titles_queue.append(seed)

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


#returns the next article that should be processed
#======================================
def choose_article():
	#eventually use Amazon SQS
	return titles_queue.pop()


#get the data from online and prepare it for later processing
#adds new links to the queue
#returns the article's text
#=======================================
def process_article(article_title):

	print article_title

	html_tree = lxml.html.parse(URL_ROOT + article_title)
	paragraph_tags = html_tree.xpath("//p")
	paragraphs = [p.text_content() for p in paragraph_tags]

	content = ""
	for p in paragraphs:
		content += (p + "\n\n")

	return content


#download the list of links in the article and add them to the queue
def process_links(article_title):
	links_tree = lxml.etree.parse(LINKS_ROOT + article_title)
	link_nodes = links_tree.xpath("//pl[@ns='0' and @exists='']")
	links = [l.text for l in link_nodes]

	#add links to the queue if they haven't been seen before
	#============================================
	for title in links:
		if (not status.has_key(title)):
			titles_queue.appendleft(title)
			status[title] = 0

	#mark the article as processed
	status[article_title] = 1


#determine text difficulty
#=============================
def determine_difficulty(text):
	print "determining difficulty"
	return 0


#save an article to a local file for eventual upload to S3
#==============================
def update_archive(article_title, content):
	archive[article_title] = content


#upload the article texts to S3
#=============================
def upload_archive():
	print "uploading to S3"



############################################################################
# Script
############################################################################

#global variables and constants
seed_list = ["Boat"]
URL_ROOT = ""
LINKS_ROOT = ""
titles_queue = deque()
status = dict()
archive = dict()
last_archive_time = datetime.datetime.now()

init("english", seed_list)

articles_processed = 0
while (articles_processed < 30):
	article = choose_article()
	words = process_article(article)
	process_links(article)
	difficulty = determine_difficulty(words)
	update_archive(article, words)	
	articles_processed += 1
	
	#see if it has been long enough to backup data to S3
	current_time = datetime.datetime.now()
	time_since_backup = current_time - last_archive_time
	if (time_since_backup.seconds >= 3600):
		upload_archive()
		last_archive_time = current_time
	
