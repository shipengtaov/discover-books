# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from os import path

ROOT_DIR = path.dirname(path.dirname(path.abspath(__file__)))
LOGS_DIR = path.join(ROOT_DIR, 'logs')
CRAWLER_DIR = path.join(ROOT_DIR, 'crawler')

COOKIE_FILE = path.join(CRAWLER_DIR, 'douban_cookie.txt')

MAX_CRAWL_COUNT = 1000

NEO4J_URI = 'bolt://localhost:7687'
# (username, password)
NEO4J_AUTH = ('your username', 'your password')

USER_AGENTS = (
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100 101 Firefox/22.0',
    'Mozilla/5.0 (Windows NT 6.1; rv:11.0) Gecko/20100101 Firefox/11.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/536.5 (KHTML, like Gecko)'
        'Chrome/19.0.1084.46 Safari/536.5',
    'Mozilla/5.0 (Windows; Windows NT 6.1) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.46'
        'Safari/536.5',
)
