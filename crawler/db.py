# -*- coding: utf-8 -*-

from neo4j.v1 import GraphDatabase

from . import config

neo4j_driver = GraphDatabase.driver(config.NEO4J_URI, auth=config.NEO4J_AUTH)


def does_crawled_before(book_id, label='DOUBAN_BOOK'):
    """判断是否已抓取过book_id
    """
    with neo4j_driver.session() as session:
        result = session.run("MATCH (n:{label} {{book_id:{value}}}) return n limit 1".format(
            label=label,
            value=book_id))
    data = result.data()
    if not data:
        return False
    # 判断是否有标题，用来确定是否抓取过此书
    if 'title' not in data[0]['n']:
        return False
    return True
