import lxml.html
import lxml.xml

def process_article():

	#get an article from the queue
	#=============================================================
	#eventually use Amazon SQS

	url_root = "http://en.wikipedia.org/wiki/"
	links_root = "http://en.wikipedia.org/w/api.php?action=parse&format=xml&prop=links&page="

	article_name = "Boat"



	#get and prepare the links and text from wikipedia
	#=============================================================

	htmltree = lxml.html.parse(url_root + article_name)

	paragraphs = htmltree.xpath('//p')
	content = [p.text_content() for p in paragraphs]

	
	linkstree = lxml.xml.parse(links_root + article_name)

	links = linkstree.xpath('//pl'


	#add links to the queue if they haven't been processed already
	#=============================================================




	#determine text difficulty
	#=============================================================



	#add text to the database
	#=============================================================
	for p in content:
		print p


process_article()
