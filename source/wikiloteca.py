import lxml.etree
import lxml.html
from collections import deque


def init(language, seed_list):
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
#===================================
def choose_article():
	#eventually use Amazon SQS
	return titles_queue.pop()


#get the data from online and prepare it for later processing
#adds new links to the queue
#returns the article's text
#========================
def process_article(article_title):

	print article_title

	#get and prepare the links and text from wikipedia
	#====================================

	#text
	html_tree = lxml.html.parse(URL_ROOT + article_title)

	paragraph_tags = html_tree.xpath("//p")
	paragraphs = [p.text_content() for p in paragraph_tags]

	content = ""
	for p in paragraphs:
		content += (p + "\n\n")


	#links
	links_tree = lxml.etree.parse(LINKS_ROOT + article_title)
	
	link_nodes = links_tree.xpath("//pl[@ns='0' and @exists='']")
	links = [l.text for l in link_nodes]


	#add links to the queue if they haven't been seen before
	#============================================
	for title in links:
		if (not status.has_key(title)):
			titles_queue.append(title)
			status[title] = 0

	
	status[article_title] = 1

	return content


#determine text difficulty
#==================
def determine_difficulty(text):
	print "text"


def update_archive(article_title, content):
	archive[article_title] = content


#global variables and constants
seed_list = ["Boat"]
URL_ROOT = ""
LINKS_ROOT = ""
titles_queue = deque()
status = dict()
archive = dict()

init("english", seed_list)

articles_processed = 0
while (articles_processed < 30):
	article = choose_article()
	words = process_article(article)
	update_archive(article, words)	
	articles_processed += 1
