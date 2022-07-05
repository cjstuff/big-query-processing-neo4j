
from neo4j import GraphDatabase


class Neo4JDriver:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    # returns all authors in the Database
    def get_all_authors(self):
        cypher = "MATCH(a:Author) " \
                 "RETURN COLLECT(a.name) AS AUTHORS"
        return self._exec_cypher_query(self, cypher)

    # returns all research articles in the Database
    def get_all_research_articles(self):
        cypher = "MATCH(b:Article) " \
                 "RETURN COLLECT(b.title) AS RESEARCH_ARTICLES"
        return self._exec_cypher_query(self, cypher)

    # given a keyword, returns all authors who
    # work on a Research Topic related to that keyword
    def get_authors(self, keyword):
        cypher = "MATCH(a:Author)-[:AUTHOR]->(b:Article) " \
                 "WHERE b.title =~ '(?i).*" + keyword + ".*' " \
                 "RETURN COLLECT(a.name) AS AUTHORS"
        return self._exec_cypher_query(self, cypher)

    # Given the author name,
    # return all research articles published by this author
    def get_research_articles(self, author_name):
        cypher = "MATCH (a:Author)-[:AUTHOR]->(b:Article) " \
                 "WHERE a.name =~ '(?i).*" + author_name + ".*' " \
                 "RETURN COLLECT(b.title) AS RESEARCH_ARTICLES"
        return self._exec_cypher_query(self, cypher)

    # Given the author name
    # return all co-authors who have worked with this author
    def get_co_authors(self, author_name):
        cypher = "MATCH (a:Author)-[:CO_AUTHOR]->(b:Author) " \
                 "WHERE b.name =~ '(?i).*" + author_name + ".*' " \
                 "RETURN COLLECT(a.name) AS CO_AUTHORS"
        return self._exec_cypher_query(self, cypher)

    # Given the author name
    # return the count of research articles published.
    def get_author_article_count(self, author_name):
        cypher = "MATCH (a:Author)-[:AUTHOR]->(b:Article) " \
                 "WHERE a.name =~ '(?i).*" + author_name + ".*' " \
                 "RETURN COUNT(b)"
        return self._exec_cypher_query(self, cypher)

    @staticmethod
    def _exec_cypher_query(self, cypher):
        with self.driver.session() as session:
            r = session.run(cypher)
            # returns a dictionary
            json = [dict(i) for i in r]
            res = list()
            for entry in json:
                for value in entry.values():
                    res.append(value)
            return res[0]


# [1] Keyword Discovery
def keyword_discovery(driver, keyword):
    authors = driver.get_authors(keyword)
    print("KEYWORD DISCOVERY:")
    for author in authors:
        print(author)
    print()


# [2] Researcher Profiling
def researcher_profiling(driver, author_name):
    research_articles = driver.get_research_articles(author_name)
    co_authors = driver.get_co_authors(author_name)
    print("RESEARCHER PROFILE:")
    print("Author: " + str(author_name))
    print("Published Research Articles: " + str(research_articles))
    print("Co-Authors: " + str(co_authors))
    print()


# [3] Influential Author
def influential_authors(driver, article):
    authors = driver.get_authors(article)
    author_dict = dict()
    for author in authors:
        score = driver.get_author_article_count(author) / len(authors)
        author_dict[author] = score
    print("MOST INFLUENTIAL AUTHOR(S):")
    for author in author_dict:
        print("Author: " + author + ", Score: " + str(author_dict[author]))


if __name__ == '__main__':
    uri = "bolt://localhost:7687"
    username = "neo4j"
    password = "1234"
    driver = Neo4JDriver(uri, username, password)

    if driver:
        print("Connected to Neo4J !")
        print()

    # get all authors in the Database
    author_list = driver.get_all_authors()

    # Get all research articles in the Database
    research_articles_list = driver.get_all_research_articles()

    while True:
        print("+--------------------------+\n"
              "[1] Keyword Discovery\n"
              "[2] Researcher Profiling\n"
              "[3] Influential Author\n"
              "[4] Exit")
        ch = input("Enter your choice: ")
        if ch == "1":
            keyword = input("Enter a keyword: ")
            keyword_discovery(driver, keyword)
        elif ch == "2":
            author_name = input("Enter an author name (or keyword): ")
            researcher_profiling(driver, author_name)
        elif ch == "3":
            article = input("Enter a research article name (or keyword): ")
            influential_authors(driver, article)
        elif ch == "4":
            break
        else:
            print("Invalid choice! Please try again...")

    driver.close()
