import time

from neo4j import GraphDatabase


class Neo4JDriver:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    # returns all author ids in the Database
    def get_all_author_ids(self):
        cypher = "MATCH(a:Author) " \
                 "RETURN COLLECT(ID(a)) AS AUTHOR_IDS"
        return self._exec_cypher_query(self, cypher)

    # returns all research article indexes in the Database
    def get_all_research_article_indexes(self):
        cypher = "MATCH(b:Article) " \
                 "RETURN COLLECT(b.index) AS RESEARCH_ARTICLE_INDEXES"
        return self._exec_cypher_query(self, cypher)

    # given a keyword, return a list
    # containing IDs of Authors whose names match with that keyword
    def get_author_ids_by_keyword(self, keyword):
        cypher = "MATCH(a:Author) " \
                 "WHERE a.name =~ '(?i).*" + keyword + ".*' " \
                 "RETURN COLLECT(ID(a)) AS AUTHORS"
        return self._exec_cypher_query(self, cypher)

    # given a keyword, return a list
    # containing all Research Article Indexes related to that keyword.
    def get_research_article_indexes_by_keyword(self, keyword):
        cypher = "MATCH(b:Article) " \
                 "WHERE b.title =~ '(?i).*" + keyword + ".*' " \
                 "RETURN COLLECT(b.index) AS RESEARCH_ARTICLES"
        return self._exec_cypher_query(self, cypher)

    # Given a Research Article Index, return a list
    # containing all Author IDs working on that Research Article
    def get_author_ids_by_research_article_index(self, research_article_index):
        cypher = "MATCH(a:Author)-[:AUTHOR]->(b:Article) " \
                 "WHERE b.index = '" + research_article_index + "' " \
                 "RETURN COLLECT(ID(a)) AS AUTHORS"
        return self._exec_cypher_query(self, cypher)

    # Given the Author ID, return a list
    # containing all Research Article Indexes published by this author
    def get_research_article_indexes_by_author_id(self, author_id):
        cypher = "MATCH (a:Author)-[:AUTHOR]->(b:Article) " \
                 "WHERE ID(a) = " + str(author_id) + " " \
                 "RETURN COLLECT(b.index) AS RESEARCH_ARTICLE_INDEXES"
        return self._exec_cypher_query(self, cypher)

    # Given the Author ID, return the Author name
    def get_author_name_by_author_id(self, author_id):
        cypher = "MATCH (a:Author) " \
                 "WHERE ID(a) = " + str(author_id) + " " \
                 "RETURN a.name"
        return self._exec_cypher_query(self, cypher)

    # Given the Research Article Index,
    # return the full Research Article Title
    def get_research_article_title_by_research_article_index(self, research_article_index):
        cypher = "MATCH (b:Article) " \
                 "WHERE (b.index) = '" + research_article_index + "' " \
                 "RETURN b.title"
        return self._exec_cypher_query(self, cypher)

    # Given the Author ID,
    # return all Co-Author IDs who have worked with this Author
    def get_co_author_ids_by_author_id(self, author_id):
        cypher = "MATCH (a:Author)-[:CO_AUTHOR]->(b:Author) " \
                 "WHERE ID(b) = " + str(author_id) + " " \
                 "RETURN COLLECT(ID(a)) AS CO_AUTHOR_IDS"
        return self._exec_cypher_query(self, cypher)

    # Given the Author ID,
    # return the count of Research Articles published by this author.
    def get_author_article_count(self, author_id):
        cypher = "MATCH (a:Author)-[:AUTHOR]->(b:Article) " \
                 "WHERE ID(a) = " + str(author_id) + " " \
                 "RETURN COUNT(b)"
        return self._exec_cypher_query(self, cypher)

    # Given two author IDs, create CO_AUTHOR relationship
    def add_co_author_relationship(self, from_author_id, to_author_id):
        cypher = "MATCH (a:Author), (b:Author) " \
                 "WHERE ID(a) = " + str(from_author_id) + " " \
                   "AND ID(b) = " + str(to_author_id) + " " \
                 "CREATE (a)-[r:CO_AUTHOR]->(b)"
        self._write_cypher_query(self, cypher)

    @staticmethod
    def _exec_cypher_query(self, cypher):
        with self.driver.session() as session:
            r = session.run(cypher)
            # convert to json format
            json = [dict(i) for i in r]
            # json to list convert
            res = list()
            for entry in json:
                for value in entry.values():
                    res.append(value)
            # return list
            return res[0]

    @staticmethod
    def _write_cypher_query(self, cypher):
        with self.driver.session() as session:
            r = session.run(cypher)


# Given a list of Author IDs
# return a list containing respective Author names
def author_ids_to_author_names(driver, author_ids):
    author_names = list()
    for author_id in author_ids:
        name = str(driver.get_author_name_by_author_id(author_id))
        author_names.append(name)
    return author_names


# Given a list of Research Article Indexes
# return a list containing respective Research Article Titles
def research_article_indexes_to_research_article_titles(driver, research_article_indexes):
    research_article_titles = list()
    for research_article_index in research_article_indexes:
        title = str(
            driver.get_research_article_title_by_research_article_index(
                research_article_index
            )
        )
        research_article_titles.append(title)
    return research_article_titles


# Check if the given author (as ID) has published the given research article (as index)
def has_published_article(driver, author_id, research_article_index):
    research_article_indexes = driver.get_research_article_indexes_by_author_id(author_id)
    for index in research_article_indexes:
        if research_article_index == index:
            return True
    return False


# Creates CO_AUTHOR relationship between authors
# that have collaborated together to publish at least one research article.
def create_co_author_relationship(driver, author_ids):
    # create a boolean table to mark if this author has been explored
    explored = dict()
    for author_id in author_ids:
        explored[author_id] = False
        # get all research article indexes published by this author
        research_article_indexes = driver.get_research_article_indexes_by_author_id(author_id)
        # create a boolean table so that we can mark the authors as visited if CO_AUTHOR relation exists.
        visited = dict()
        # for each such article, find out other authors (if any)
        for research_article_index in research_article_indexes:
            other_author_ids = driver.get_author_ids_by_research_article_index(research_article_index)
            for other_author_id in other_author_ids:
                if author_id == other_author_id:
                    continue
                if other_author_id in explored and explored[other_author_id] is True:
                    continue
                if other_author_id not in visited:
                    visited[other_author_id] = False
                if visited[other_author_id] is True:
                    continue
                # we'll make the author with lesser published articles
                # as co-author to the author with more published articles
                count_i = driver.get_author_article_count(author_id)
                count_j = driver.get_author_article_count(other_author_id)
                if int(count_i) > int(count_j):
                    driver.add_co_author_relationship(other_author_id, author_id)
                else:
                    driver.add_co_author_relationship(author_id, other_author_id)
                visited[other_author_id] = True
        explored[author_id] = True


# [1] Keyword Discovery
def keyword_discovery(driver, keyword):
    i = 1
    print("KEYWORD DISCOVERY:")
    research_article_indexes = driver.get_research_article_indexes_by_keyword(keyword)
    for research_article_index in research_article_indexes:
        print("[" + str(i) + "]")
        research_article = driver.get_research_article_title_by_research_article_index(
            research_article_index
        )
        print("Research Article: " + str(research_article))
        author_ids = driver.get_author_ids_by_research_article_index(research_article_index)
        print("Authors: " + str(author_ids_to_author_names(driver, author_ids)))
        print("Total authors working on this Research Article:", len(author_ids))
        print()
        i = i + 1
    print()


# [2] Researcher Profiling
def researcher_profiling(driver, keyword):
    i = 1
    print("RESEARCHER PROFILE:")
    author_ids = driver.get_author_ids_by_keyword(keyword)
    for author_id in author_ids:
        print("[" + str(i) + "]")
        research_article_indexes = driver.get_research_article_indexes_by_author_id(author_id)
        co_author_ids = driver.get_co_author_ids_by_author_id(author_id)
        print("Author Name: " + str(driver.get_author_name_by_author_id(author_id)))
        print("Published Research Articles: " + str(
            research_article_indexes_to_research_article_titles(driver, research_article_indexes))
        )
        print("Total no. of Research Articles published: " + str(len(research_article_indexes)))
        print("Co-Authors: " + str(author_ids_to_author_names(driver, co_author_ids)))
        print("Total no. of Co-authors: " + str(len(co_author_ids)))
        print()
        i = i + 1
    print()


# [3] Influential Authors
def influential_authors(driver, keyword):
    i = 1
    print("INFLUENTIAL AUTHORS:")
    research_article_indexes = driver.get_research_article_indexes_by_keyword(keyword)
    for research_article_index in research_article_indexes:
        print("[" + str(i) + "]")
        research_article_title = driver.get_research_article_title_by_research_article_index(research_article_index)
        print("Research Article: " + str(research_article_title))
        author_ids = driver.get_author_ids_by_research_article_index(research_article_index)
        author_dict = dict()
        for author_id in author_ids:
            page_rank = driver.get_author_article_count(author_id) / len(author_ids)
            author_dict[author_id] = page_rank
        print("Most Influential Author(s):")
        for author_id in author_dict:
            print("Author: " + str(driver.get_author_name_by_author_id(author_id)) +
                  ", Page Rank: " + str(author_dict[author_id]))
        print()
        i = i + 1
    print()


if __name__ == '__main__':

    uri = "bolt://localhost:7687"
    username = "neo4j"
    password = "1234"
    driver = Neo4JDriver(uri, username, password)

    if driver:
        print("Connected to Neo4J !")
        print()

    # get all author ids in the Database
    author_id_list = driver.get_all_author_ids()

    # Get all research article indexes from the Database
    research_article_index_list = driver.get_all_research_article_indexes()

    print("Total no. of Authors: " + str(len(author_id_list)))
    print("Total no. of Research Articles: " + str(len(research_article_index_list)))

    print()

    # # Initialization Step
    # print("Creating Co-Author relationship...")
    # start = time.time()
    # create_co_author_relationship(driver, author_id_list)
    # end = time.time()
    # print("Co_Author Relationship successfully created.")
    # print("Total time elapsed: " + str(end - start) + " secs.")

    while True:
        print("+--------------------------+\n"
              "[1] Keyword Discovery\n"
              "[2] Researcher Profiling\n"
              "[3] Influential Author\n"
              "[4] Exit")
        ch = input("Enter your choice: ")
        if ch == "1":
            keyword = input("Enter a research article name (or keyword): ")
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
