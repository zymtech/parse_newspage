#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-01-10 11:44:51
# Project: doc
import lxml.html
import lxml.etree
from pyquery import PyQuery

try:
    from requests.utils import get_encodings_from_content
except ImportError:
    get_encodings_from_content = None
import lxml.html
import lxml.etree


def doc(html,url):
    """Returns a PyQuery object of a request's content"""
    parser = lxml.html.HTMLParser(encoding='utf-8')
    elements = lxml.html.fromstring(html, parser=parser)
    if isinstance(elements, lxml.etree._ElementTree):
        elements = elements.getroot()
    doc = PyQuery(elements)
    doc.make_links_absolute(url)
    return doc

