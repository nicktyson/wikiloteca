import lxml.etree
import lxml.html

def process_article():

	#get an article from the queue
	#=============================================================
	#eventually use Amazon SQS

	url_root = "http://en.wikipedia.org/wiki/"
	links_root = "http://en.wikipedia.org/w/api.php?action=parse&format=xml&prop=links&page="

	article_name = "Boat"



	#get and prepare the links and text from wikipedia
	#=============================================================

	#text
	htmltree = lxml.html.parse(url_root + article_name)

	paragraphs = htmltree.xpath("//p")
	content = [p.text_content() for p in paragraphs]


	#links
	linkstree = lxml.etree.parse(links_root + article_name)
	
	linknodes = linkstree.xpath("//pl[@ns='0']")
	links = [l.text for l in linknodes]
	for title in links:
		print title


	#add links to the queue if they haven't been processed already
	#=============================================================




	#determine text difficulty
	#=============================================================



	#add text to the database
	#=============================================================
	for p in content:
		print p


process_article()
