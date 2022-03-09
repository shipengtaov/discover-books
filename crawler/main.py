#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from os import path
from argparse import ArgumentParser
import time
from threading import Thread, Lock, Event
from multiprocessing import Queue
import random
import traceback

import requests
import lxml

from . import config
from . import utils
from . import db
from .db import neo4j_driver


logger = utils.get_logger('crawler', path.join(config.LOGS_DIR, 'crawler.log'))
# 当前抓了多少本书
CURRENT_COUNT = 0
CURRENT_COUNT_LOCK = Lock()


class Crawler(Thread):
    def __init__(self, queue, run_event, max_count):
        super(Crawler, self).__init__()
        self.deamon = True
        self.queue = queue
        self.run_event = run_event
        self.max_count = max_count

    def run(self):
        global CURRENT_COUNT
        while self.run_event.is_set():
            if CURRENT_COUNT > 0:
                logger.debug('当前已抓取 {}/{} 本书'.format(CURRENT_COUNT, self.max_count))
            if CURRENT_COUNT >= self.max_count:
                break
            if self.queue.empty():
                logger.debug('no task')
                time.sleep(3)
                continue
            try:
                referer_url, url = self.queue.get()
                book_id = utils.get_book_id_from_url(url)
                assert book_id, '未能从 url: <{}> 中提取出book_id'.format(url)

                # 判断数据库是否已存在
                if db.does_crawled_before(book_id):
                    logger.debug('数据库中已存在book_id: {}, url: {}'.format(book_id, url))
                    continue

                logger.debug('正在抓取 {}'.format(url))
                headers = {
                    'User-Agent': random.choice(config.USER_AGENTS),
                }
                response = requests.get(url, headers=headers, timeout=10)
                assert response.ok, '{} status code error: {}'.format(url, response.status_code)

                parse_book = utils.parse_book(response)

                with neo4j_driver.session() as s:
                    cypher = """MERGE (n:DOUBAN_BOOK {{book_id: {book_id}}})
                        ON CREATE SET n.book_id=toInteger({book_id}),
                                      n.title="{title}",
                                      n.url="{url}",
                                      n.author="{author}",
                                      n.press="{press}",
                                      n.publish_date="{publish_date}",
                                      n.price="{price}"
                        ON MATCH SET n.title="{title}",
                                      n.url="{url}",
                                      n.author="{author}",
                                      n.press="{press}",
                                      n.publish_date="{publish_date}",
                                      n.price="{price}"
                    """.format(
                        book_id=book_id,
                        title=parse_book['title'],
                        url=url,
                        author=parse_book['author'],
                        press=parse_book['press'],
                        publish_date=parse_book['publish_date'],
                        price=parse_book['price'])
                    s.run(cypher)

                    # 建立 relation
                    if referer_url:
                        referer_book_id = utils.get_book_id_from_url(referer_url)
                        cypher = """MATCH
                            (m:DOUBAN_BOOK {{book_id: {referer_book_id}}}),
                            (n:DOUBAN_BOOK {{book_id: {book_id}}})
                        MERGE (m)-[:RELATE]->(n)
                        """.format(referer_book_id=referer_book_id,
                                   book_id=book_id)
                        s.run(cypher)

                    for relate_book_url in parse_book['related_books']:
                        if not utils.is_douban_book_url(relate_book_url):
                            logger.debug('book {} 不是一个合法的豆瓣图书链接'.format(relate_book_url))
                            continue
                        # logger.debug('adding task: {}'.format(relate_book_url))
                        self.queue.put((url, relate_book_url))
                # 当前已经抓了多少本书
                with CURRENT_COUNT_LOCK:
                    CURRENT_COUNT += 1
                logger.debug('图书 <{}> 处理完毕'.format(url))
            except KeyboardInterrupt:
                break
            except:
                logger.error(traceback.format_exc())
                time.sleep(3)
                continue
            finally:
                # self.queue.task_done()
                # sleep，防止频繁抓取                
                time.sleep(random.random()*5)


def start_crawler(args):
    start_urls = args.urls
    max_count = args.max_count or config.MAX_CRAWL_COUNT
    thread_count = args.thread_count

    queue = Queue()
    for url in start_urls:
        if not utils.is_douban_book_url(url):
            raise SystemExit('<{}> 不是合法的豆瓣图书链接'.format(url))
        logger.debug('adding url: {}'.format(url))
        queue.put((None, url))

    run_event = Event()
    run_event.set()

    threads = []
    for i in range(thread_count):
        logger.debug('starting thread: {}/{}'.format(i+1, thread_count))
        thread = Crawler(queue=queue, run_event=run_event, max_count=max_count)
        thread.start()
        threads.append(thread)
    try:
        while True:
            if all(not t.is_alive() for t in threads):
                break
            time.sleep(.1)
    except KeyboardInterrupt:
        print('stoping all threads')
        run_event.clear()
        for t in threads:
            t.join()
        print('threads successfully closed')
    print('crawled total {} books'.format(CURRENT_COUNT))


def cli():
    parser = ArgumentParser()
    parser.add_argument('-u', '--urls', nargs='+', help='从哪些链接开始抓取')
    parser.add_argument('-C', '--max-count', type=int, help='最多抓取多少本书. 默认：{}'.format(config.MAX_CRAWL_COUNT))
    parser.add_argument('-t', '--thread-count', type=int, default=4, help='多少线程. 默认：4')
    args = parser.parse_args()

    if not args.urls:
        parser.print_help()
        raise SystemExit
    return args
