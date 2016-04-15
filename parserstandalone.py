#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import six
import json
import chardet
import lxml.html
import lxml.etree
import lxml.html.clean as clean
import dateutil.parser as dparser
import time
import datetime
import os
import tldextract
from pyquery import PyQuery
from requests.structures import CaseInsensitiveDict
from requests.utils import get_encoding_from_headers
try:
    from requests.utils import get_encodings_from_content
except ImportError:
    get_encodings_from_content = None
from requests import HTTPError
from pyspider.libs import utils


#from pyspider.libs.base_handler import *
import re
import mimetypes
import urllib2
import codecs
import json
import hashlib
import requests


def stringifyImage(url):
    if len(url) == 0:
        return ''
    img = urllib2.urlopen(url).read().encode("base64").replace("\n","")
    return img

def getsafedictvalue(dict,pathval,defval):
    childs = pathval.split("/")
    childdict = dict
    try:
        for child in childs:
            childdict = childdict[child]
        retval = childdict
    except KeyError:
        retval = defval
        pass
    return retval

def encoding(rsp):
    """
    encoding of Response.content.

    if Response.encoding is None, encoding will be guessed
    by header or content or chardet if avaibable.
    """
    # content is unicode
    if isinstance(rsp.content, six.text_type):
        return 'unicode'

    # Try charset from content-type
    encoding = get_encoding_from_headers(rsp.headers)
    if encoding == 'ISO-8859-1':
        encoding = None

    # Try charset from content
    if not encoding and get_encodings_from_content:
        encoding = get_encodings_from_content(rsp.content)
        encoding = encoding and encoding[0] or None

    # Fallback to auto-detected encoding.
    if not encoding and chardet is not None:
        encoding = chardet.detect(rsp.content)['encoding']

    if encoding and encoding.lower() == 'gb2312':
        encoding = 'gb18030'

    encoding = encoding or 'utf-8'
    return encoding

def doc(rsp):
    """Returns a PyQuery object of a request's content"""
    parser = lxml.html.HTMLParser(encoding=encoding(rsp))
    elements = lxml.html.fromstring(rsp.content, parser=parser)
    if isinstance(elements, lxml.etree._ElementTree):
        elements = elements.getroot()
    doc =PyQuery(elements)
    doc.make_links_absolute(rsp.url)
    return doc

def parse_response(response, parser):
    linkurl = response.url
    docrsp = doc(response)

    # Get a
    for CSS in parser:
        contraw = docrsp(CSS["content"]).remove("a").remove("script")
        title = docrsp(CSS["title"]).text()
        pubtimetxt = docrsp(CSS["date"]).text()
        if len(contraw.text())>0:
            break;
        if (len(contraw.text())<=0) or (len(title)<=0) or (len(pubtimetxt)<=0):
            return 0
        #raise RuntimeError("Incorrect parser: " + response.url)


    imgurl=""
    images = contraw.items('img')
    if images:
        for image in images:
            imgurl=imgurl+image.attr('src')+";"
    imgdata = ""

    cleaner = clean.Cleaner(page_structure=True)
    showcont = cleaner.clean_html(contraw.remove_attr('id').remove_attr('class').html())
    showcont = re.sub(r'id=".*?"|class=".*?"', '', showcont)
    showcont = re.sub(r'[\s+]*?>', '>', showcont)
    showcont = showcont.replace("\n","").replace("\t","").replace("<div>","").replace("</div>","")

    cleantext = contraw.text()

    pubtime = dparser.parse(pubtimetxt,fuzzy=True)#.strftime('%Y%m%d%H%M%S')
    pubtimeint = int(time.mktime(pubtime.timetuple()))

    item = {
        "url": linkurl,
        "image_url": imgurl,
        "image_data": imgdata,
        "title": title,
        "src": "",
        "tags": "",
        "pdate": pubtimeint,
        "showcontent": showcont,
        "content": cleantext,
    }
    return item

crawl_config = {
   'start_url': 'http://news.baidu.com/n?cmd=1&class=civilnews&tn=rss',
   'css_parser': './css_parser.json',
   'languagetype': 'chineseUTF8',
   'crawlername': 'pyspider',
   'DREHost': '127.0.0.1',
   'DREPort': '11001',
   'DREDbName': 'NewsCn',
   'DREKillOption': '', #default idol killmode
}




def page_parse( response ):
    with open("./css_parser.json") as data_file:
        parserTable = json.load(data_file)
        url_ext = tldextract.extract(response.url).domain
        parser = parserTable.get(url_ext,None)
        if parser is None:
            return 0
            #raise RuntimeError("No parser: " + response.url)

        if parser:
            parser = parser['parser']
            item =parse_response(response,parser)
        return item


if __name__ == '__main__':

    try:
        req = requests.get('http://www.chinanews.com/gn/2016/03-04/7783132.shtml')
        if req.status_code == 200:
            page_parse( req )
    except requests.exception.ConnectionError:
        pass
    except BaseException as e:
        print e

