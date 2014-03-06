import lxml.etree
import lxml.html
from collections import deque

#returns the next article that should be processed
#=====================
def choose_article():
	#eventually use Amazon SQS
	return titles_queue.pop()


#get the data from online and prepare it for later processing
#========================
def process_article(article_name):

	print article_name

	URL_ROOT = "http://en.wikipedia.org/wiki/"
	LINKS_ROOT= "http://en.wikipedia.org/w/api.php?action=parse&format=xml&prop=links&page="


	#get and prepare the links and text from wikipedia
	#====================================

	#text
	html_tree = lxml.html.parse(URL_ROOT + article_name)

	paragraph_tags = html_tree.xpath("//p")
	paragraphs = [p.text_content() for p in paragraph_tags]

	content = ""
	for p in paragraphs:
		content += (p + "\n\n")


	#links
	links_tree = lxml.etree.parse(LINKS_ROOT + article_name)
	
	link_nodes = links_tree.xpath("//pl[@ns='0' and @exists='']")
	links = [l.text for l in link_nodes]



	#add links to the queue if they haven't been seen before
	#============================================

	for title in links:
		if (not status.has_key(title)):
			titles_queue.append(title)
			status[title] = 0

	
	status[article_name] = 1


#determine text difficulty
#==================
def determine_difficulty(text):
	print "text"



def update_database():
	print "asdf"



status = dict(Boat = 0)
titles_queue  = deque(["Boat"])

articles_processed = 0
while (articles_processed < 30):
	article = choose_article()
	process_article(article)
	articles_processed += 1
