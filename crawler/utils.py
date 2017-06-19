# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import logging
import re

import lxml.html

from .compat import urlparse, text_type

douban_book_pattern = re.compile(r'^https?://book\.douban\.com/subject/\d+/?', re.I)
douban_book_id_pattern = re.compile(r'^https?://book\.douban\.com/subject/(\d+)/?', re.I)


def get_logger(name, filename, level=logging.DEBUG, fmt=None):
    logger = logging.Logger(name)

    fmt = fmt or '%(asctime)s-%(name)s-%(levelname)-10s%(message)s'
    formatter = logging.Formatter(fmt=fmt, datefmt='%Y-%m-%d %H:%M:%S')

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(filename)
    file_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    logger.setLevel(level)

    return logger


def is_douban_book_url(url):
    """判断是否是豆瓣图书链接
    """
    match = douban_book_pattern.match(url)
    return True if match else False


def get_book_id_from_url(url):
    match = douban_book_id_pattern.search(url)
    return int(match.group(1)) if match else None


def parse_book(response):
    """解析豆瓣图书详情页
    """
    doc = lxml.html.fromstring(response.text)

    title = ''.join([i.strip() for i in doc.xpath('//h1//text()')])

    info_html = lxml.html.tostring(doc.xpath('//*[@id="info"]')[0], encoding=text_type)
    book_info = _parse_book_info(info_html)

    related_books = _parse_book_related(response.text)

    return dict(
        title=title,
        author=book_info['author'],
        press=book_info['press'],
        publish_date=book_info['publish_date'],
        price=book_info['price'],
        related_books=related_books)


def _parse_book_info(html):
    """解析豆瓣图书信息（作者，出版社，出版年，定价）

    :param html(string): 图书信息部分的原始html
    """
    end_flag = 'END_FLAG'
    html = html.replace('<br>', end_flag)
    html = html.replace('<br/>', end_flag)

    doc = lxml.html.fromstring(html)
    text = doc.text_content()
    pattern = r'{}[:：](.*?){}'
    result = dict()
    for key, column in [
            ('author', '作者'),
            ('press', '出版社'),
            ('publish_date', '出版年'),
            ('price', '定价')]:
        result[key] = re.search(pattern.format(column, end_flag),
                                text,
                                re.I | re.DOTALL).group(1).strip()
    return result


def _parse_book_related(html):
    """获取相关图书
    """
    doc = lxml.html.fromstring(html)
    books = doc.xpath('//dl[@class=""]/dt/a')
    assert len(books) > 0, "parse related books fail. 0 related books"
    return [i.attrib['href'] for i in books]
