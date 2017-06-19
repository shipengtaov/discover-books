# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import pytest
from . import utils


@pytest.mark.parametrize('url,expected', [
    ('https://book.douban.com/subject/3112503', True),
    ('http://book.douban.com/subject/3112503/', True),
    ('https://book.douban.com/subject/3112503/test', True),

    # 这种情况也应该排除
    # ('https://book.douban.com/subject/3112503t', False),

    # 6位数字
    ('http://book.douban.com/subject/311250/', True),
    # 8位数字
    ('http://book.douban.com/subject/31125031/', True),

    ('https://book.douban.com/subject/3112503/?start=30', True),
    ('https://book.douban.com/subject/3112503?start=30', True),
])
def test_is_douban_book_url(url, expected):
    assert expected is utils.is_douban_book_url(url)


@pytest.mark.parametrize('url,expected', [
    ('https://book.douban.com/subject/3112503/', 3112503),
    ('https://book.douban.com/subject/3112503/?start=25&limit=25', 3112503),

    ('https://book.douban.com/subject/31125/', 31125),
    ('https://book.douban.com/subject/test/', None),
    ('https://another-domain.com/subject/1111', None),
])
def test_get_book_id_from_url(url, expected):
    assert expected == utils.get_book_id_from_url(url)


def test_parse_book_info():
    func = utils._parse_book_info

    html = """
    <div id="info" class>
    <span>
      <span class="pl"> 作者</span>:
        <a class="" href="/search/Wesley%20J.%20Chun">[美]Wesley J. Chun（陳仲才）</a>
    </span><br>
    <span class="pl">出版社:</span> 人民邮电出版社<br>
    <span class="pl">原作名:</span> Core Python Programming, 2nd Edition<br>
    <span>
      <span class="pl"> 译者</span>:
        <a class="" href="/search/CPUG">CPUG</a>
    </span><br>
    <span class="pl">出版年:</span> 2008-06<br>
    <span class="pl">页数:</span> 654<br>
    <span class="pl">定价:</span> 89.00元<br>
    <span class="pl">装帧:</span> 平装<br>
    <span class="pl">ISBN:</span> 9787115178503<br>
    </div>
    """
    result = func(html)
    assert result['author'] == '[美]Wesley J. Chun（陳仲才）'
    assert result['press'] == '人民邮电出版社'
    assert result['publish_date'] == '2008-06'
    assert result['price'] == '89.00元'


def test_parse_book_related():
    func = utils._parse_book_related

    html = """
    <div class="content clearfix">
    <dl class>
        <dt>
            <a href="book1_url"><img class="m_sub_img" src="book1_img"></a>
        </dt>
        <dd>
            <a href="book1_url" class="">book1 name</a>
        </dd>
    </dl>
    <dl class>
        <dt>
            <a href="book2_url"><img class="m_sub_img" src="book2_img"></a>
        </dt>
        <dd>
            <a href="book2_url" class="">book2 name</a>
        </dd>
    </dl>
    </div>
    """
    result = func(html)
    assert result == ['book1_url', 'book2_url']
