from flask import Flask, Markup, render_template, request
from gensim.parsing.preprocessing import remove_stopwords
from newsapi import NewsApiClient
from newspaper import Article
from pbwrap import Pastebin

from smmry_wrapper import SmmryAPI

# initialise api keys and flask app
print("[STATUS] initialising api connections")
news = NewsApiClient("3013d476ab43420d9edbe5a9f83f84d0")
smmry = SmmryAPI("6FD2949A59")
pb = Pastebin("iPJ_qGW_Sh85emPUXf1X1oCc0Nmh4EEk")
app = Flask(__name__)


# grab top headlines and display on homepage
@app.route("/")
def home():
    print("[STATUS] grabbing top headlines")
    top_headlines = news.get_top_headlines(country="us")
    return render_template("index.html", articles=parser(top_headlines))


# perform search based on query, if failed- return error page
@app.route("/search", methods=["POST"])
def search():
    try:
        query = request.form["query"]
        search_results = news.get_everything(q=query)
        print("[STATUS] searching for articles related to '" + query + "'")
        return render_template("search.html", articles=parser(search_results), query=query)
    except:
        print("[ERROR] search failed, recheck search terms")
        return render_template("error.html", error="nosearch")


# attempt combination based on query, if failed- return error page
@app.route("/combine", methods=["POST"])
def combine():
    try:
        query = request.form["query"]
        print("[STATUS] searching for articles related to '" + query + "'")
        search_results = news.get_everything(q=query)
        parsed_results = parser(search_results)

        text = ""
        sources = []

        print("[STATUS] combining top 3 articles about '" + query + "'")
        for article_num in range(3):
            np_article = Article(parsed_results[article_num].url)
            np_article.download()
            np_article.parse()
            text += np_article.text
            sources.append(parsed_results[article_num])

        print("[STATUS] creating pastebin link")
        paste_link = pb.create_paste(text)

        print("[INFO] pastebin link: " + paste_link)
        s = smmry.summarize(paste_link, sm_with_break="<br><br>", sm_keyword_count=5)

        return render_template(
            "combine.html",
            summary=Markup(rreplace(s.sm_api_content, "<br>", "", 2)),
            img=parsed_results[0].img,
            title=query,
            keywords=s.sm_api_keyword_array,
            fulltext=remove_stopwords(text),
            sources=sources
        )
    except:
        return render_template("error.html", error="nocombine")


# attempt summarization,
# if failed- attempt extraction using newspaper,
#   if failed- show error page
@app.route("/article", methods=["POST"])
def article_page():
    link = request.form["link"]
    img = request.form["img"]
    title = request.form["title"]
    print("[STATUS] displaying article: " + title)

    try:
        try:
            s = smmry.summarize(link, sm_with_break="<br><br>", sm_keyword_count=5)
        except:
            print("[WARNING] couldn't extract article with smmry, switch to newspaper")
            np_article = Article(link)
            np_article.download()
            np_article.parse()

            print("[STATUS] creating pastebin link")
            paste_link = pb.create_paste(np_article.text)
            print("[STATUS] link created successfully: " + paste_link)

            s = smmry.summarize(
                paste_link, sm_with_break="<br><br>", sm_keyword_count=5
            )

        parsed_summary = Summary(
            Markup(rreplace(s.sm_api_content, "<br>", "", 2)),
            s.sm_api_title,
            s.sm_url,
            s.sm_api_content_reduced,
            s.sm_api_keyword_array,
        )

        return render_template(
            "article.html", summary=parsed_summary, link=link, img=img, title=title
        )
    except:
        return render_template("error.html", link=link, img=img, title=title)


def rreplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)


# summary class
class Summary:
    def __init__(self, summarised_text, title, link, percentage_reduced, keywords):
        self.summarised_text = summarised_text
        self.title = title
        self.link = link
        self.percentage_reduced = percentage_reduced
        self.keywords = keywords


# article class
class ArticleObj:
    def __init__(self, author, pub, title, desc, img, url):
        self.author = author
        self.pub = pub
        self.title = title
        self.desc = desc
        self.img = img
        self.url = url


# news api parser
def parser(article_obj):
    articles = []

    for article_num in range(20):
        author = article_obj["articles"][article_num]["author"]
        pub = article_obj["articles"][article_num]["source"]["name"]
        title = article_obj["articles"][article_num]["title"]
        desc = article_obj["articles"][article_num]["description"]
        img = article_obj["articles"][article_num]["urlToImage"]
        url = article_obj["articles"][article_num]["url"]

        # exclude articles with no images or authors
        if (img is not None) and (author is not None):
            articles.append(ArticleObj(author, pub, title, desc, img, url))

    return articles


if __name__ == "__main__":
    app.run(debug=True)
