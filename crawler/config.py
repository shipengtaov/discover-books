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
