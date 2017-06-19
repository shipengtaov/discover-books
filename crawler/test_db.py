# -*- coding: utf-8 -*-

from .db import neo4j_driver
from .db import does_crawled_before


def test_does_crawled_before():
    try:
        label = 'DISCOVER_BOOKS_TEST_DOUBAN_BOOK'
        assert does_crawled_before(12345, label=label) is False

        with neo4j_driver.session() as session:
            session.run('create (:{} {{book_id: 12345, url:"https://book.douban.com/subject/111"}})'.format(label))
        assert does_crawled_before(12345, label=label) is False
        with neo4j_driver.session() as session:
            session.run('match (n:{} {{book_id: 12345}}) delete n'.format(label))
        assert does_crawled_before(12345, label=label) is False

        with neo4j_driver.session() as session:
            session.run('create (:{} {{book_id: 12345, title: "Brave New World"}})'.format(label))
        assert does_crawled_before(12345678, label=label) is False
        assert does_crawled_before(12345, label=label) is True
        with neo4j_driver.session() as session:
            session.run('match (n:{} {{book_id: 12345}}) delete n'.format(label))
        assert does_crawled_before(12345, label=label) is False
    finally:
        with neo4j_driver.session() as session:
            session.run('match (n:{}) detach delete n'.format(label))
