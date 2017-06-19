# -*- coding: utf-8 -*-

import sys

if sys.version_info.major < 3:
    text_type = unicode
    from urlparse import urlparse, urljoin
else:
    text_type = str
    from urllib.parse import urlparse, urljoin
