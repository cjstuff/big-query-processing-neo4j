# import Flask ::: for implementig flask server
import json
import os

from flask import Flask, render_template, request, jsonify
from neoa import *

uri = "bolt://localhost:7687"
username = "neo4j"
password = "1234"
driver = Neo4JDriver(uri, username, password)

# create a new web-app whixh is a Flask application while __name__	represents that his is
# the file that will reresent the web-app
app = Flask(__name__, static_url_path='/static')


# / represent the default page localhost/
@app.route("/")
def main():
    return render_template("main.html")


@app.route("/keyword_discover")
def keyword_discover():
    return render_template("second_keyword_discovery.html")


@app.route("/research_profile")
def research_profile():
    return render_template("third_researcher_profiling.html")


@app.route("/influential_author")
def influential_author():
    return render_template("fourth_influential_authors.html")


@app.route("/authors", methods=["get"])
# Declarator function
def get_authors():
    author_list = list()
    author_ids = driver.get_all_author_ids()
    for author_id in author_ids:
        author_list.append(driver.get_author_name_by_author_id(author_id))

    return render_template("output.html", authors=author_list)


'''
@app.route("/get_unique_authors", methods=["post"])
def get_unique_authors():
    keyword = request.form.get("keyword")
    # authors = driver.get_authors(keyword)
    # print("KEYWORD DISCOVERY:")
    # output = list()
    # for author in authors:
    #	print(author)
    #	output.append(author)
    # return authors
    author_list.append(keyword)
    author_list.append(keyword)
    return render_template("output.html", authors=author_list)


# return json.dumps(keyword)
'''


@app.route("/keyword_discovery", methods=["post"])
def keyword_discovery():
    keyword = request.form.get("keyword")
    i = 1
    output_dict = {"output": []}
    print("KEYWORD DISCOVERY:")
    research_article_indexes = driver.get_research_article_indexes_by_keyword(keyword)
    for research_article_index in research_article_indexes:
        # print("[" + str(i) + "]")
        research_article = driver.get_research_article_title_by_research_article_index(
            research_article_index
        )
        # print("Research Article: " + str(research_article))
        author_ids = driver.get_author_ids_by_research_article_index(research_article_index)
        # print("Authors: " + str(author_ids_to_author_names(driver, author_ids)))
        # print("Total authors working on this Research Article:", len(author_ids))
        # print()
        authors = author_ids_to_author_names(driver, author_ids)
        outs = {"Research_Article": research_article,
                "Authors": authors,
                "No_of_Authors": len(author_ids)
                }
        output_dict["output"].append(outs)
        i = i + 1

    return render_template("output.html", authors=output_dict["output"])


@app.route("/researcher_profiling", methods=["post"])
def researcher_profiling():
    keyword = request.form.get("keyword")
    i = 1
    output_dict = {"output": []}
    print("RESEARCHER PROFILE:")
    author_ids = driver.get_author_ids_by_keyword(keyword)
    for author_id in author_ids:
        print("[" + str(i) + "]")
        research_article_indexes = driver.get_research_article_indexes_by_author_id(author_id)
        co_author_ids = driver.get_co_author_ids_by_author_id(author_id)
        # print("Author Name: " + str(driver.get_author_name_by_author_id(author_id)))
        # print("Published Research Articles: " + str(
        #     research_article_indexes_to_research_article_titles(driver, research_article_indexes))
        #       )
        # print("Total no. of Research Articles published: " + str(len(research_article_indexes)))
        # print("Co-Authors: " + str(author_ids_to_author_names(driver, co_author_ids)))
        # print("Total no. of Co-authors: " + str(len(co_author_ids)))

        authors = driver.get_author_name_by_author_id(author_id)
        research_article = research_article_indexes_to_research_article_titles(driver, research_article_indexes)
        co_authors = author_ids_to_author_names(driver, co_author_ids)
        outs = {"Authors": authors,
                "Research_Article": research_article,
                "No_of_Res_articles": len(research_article),
                "No_of_Authors": len(author_ids),
                "Co_Authors": co_authors,
                "No_of_co_auth": len(co_authors)
                }
        output_dict["output"].append(outs)
        i = i + 1

    return render_template("output2.html", authors=output_dict["output"])


@app.route("/influential_authors", methods=["post"])
def influential_authors():
    keyword = request.form.get("keyword")
    i = 1
    output_dict = {"output": []}
    print("INFLUENTIAL AUTHORS:")
    research_article_indexes = driver.get_research_article_indexes_by_keyword(keyword)
    for research_article_index in research_article_indexes:
        # print("[" + str(i) + "]")
        research_article_title = driver.get_research_article_title_by_research_article_index(research_article_index)
        # print("Research Article: " + str(research_article_title))
        author_ids = driver.get_author_ids_by_research_article_index(research_article_index)
        author_dict = dict()
        for author_id in author_ids:
            page_rank = driver.get_author_article_count(author_id) / len(author_ids)
            author_dict[author_id] = page_rank
        # print("Most Influential Author(s):")
        # for author_id in author_dict:
        #     print("Author: " + str(driver.get_author_name_by_author_id(author_id)) +
        #           ", Page Rank: " + str(author_dict[author_id]))
        print()
        for author_id in author_dict:
            influential_author = driver.get_author_name_by_author_id(author_id)
            page_rank = author_dict[author_id]
            outs = {"Research_Article": research_article_title,
                    "Most_Influential_Author": influential_author,
                    "Page_Rank": page_rank
                    }
            output_dict["output"].append(outs)
        i = i + 1
    return render_template("output3.html", authors=output_dict["output"])


if __name__ == '__main__':
    os.environ['FLASK_ENV'] = 'development'  # HARD CODE since default is production
    app.run()
