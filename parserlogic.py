# -*- coding: utf-8 -*-

from parsedate import *
import re
import urllib2
import json
import lxml.html.clean as clean
import dateutil
import time
import datetime
import tldextract
import dateparser
import articleDateExtractor
from doc import doc
from getsafedictvalue import getsafedictvalue
from newspaper import *



class cx_extractor:
    """cx_extractor implemented in Python"""

    __text = []
    __threshold = 86
    __indexDistribution = []
    __blocksWidth = 3

    def getText(self,content):
        lines = content.split('\n')
        #self.__indexDistribution.clear()
        self.__indexDistribution[:]=[]
        self.__text[:]=[]
        for i in range(0,len(lines) - self.__blocksWidth):
            wordsNum = 0
            for j in range(i,i + self.__blocksWidth):
                lines[j] = lines[j].replace("\\s", "")
                wordsNum += len(lines[j])
            self.__indexDistribution.append(wordsNum)
        start = -1
        end = -1
        boolstart = False
        boolend = False
        for i in range(len(self.__indexDistribution)-1):
            if(self.__indexDistribution[i] > self.__threshold and (not boolstart)):
                if (self.__indexDistribution[i + 1] != 0 or self.__indexDistribution[i + 2] != 0 or self.__indexDistribution[i + 3] != 0):
                    boolstart = True
                    start = i
                    continue
            if (boolstart):
                if (self.__indexDistribution[i] == 0 or self.__indexDistribution[i + 1] == 0):
                    end = i
                    boolend = True
            tmp = []
            if(boolend):
                for ii in range(start,end+1):
                    if(len(lines[ii])<5):
                        continue
                    tmp.append(lines[ii]+"\n")
                str = "".join(list(tmp))
                if (u"Copyright" in str or u"版权所有" in str):
                    continue
                self.__text.append(str)
                boolstart = boolend = False
        result = "".join(list(self.__text))
        return result

    def replaceCharEntity(self,htmlstr):
        CHAR_ENTITIES={'nbsp':' ','160':' ',
                    'lt':'<','60':'<',
                    'gt':'>','62':'>',
                    'amp':'&','38':'&',
                    'quot':'"','34':'"',}
        re_charEntity=re.compile(r'&#?(?P<name>\w+);')
        sz=re_charEntity.search(htmlstr)
        while sz:
            entity=sz.group()
            key=sz.group('name')
            try:
                htmlstr=re_charEntity.sub(CHAR_ENTITIES[key],htmlstr,1)
                sz=re_charEntity.search(htmlstr)
            except KeyError:
                #以空串代替
                htmlstr=re_charEntity.sub('',htmlstr,1)
                sz=re_charEntity.search(htmlstr)
        return htmlstr

    def getHtml(self,url):
        page = urllib2.urlopen(url) #urllib.request.urlopen(url)
        html = page.read()
        return html.decode("GB18030")

    def readHtml(self,path):
        page = open(path,encoding='GB18030')
        lines = page.readlines()
        s = ''
        for line in lines:
            s+=line
        page.close()
        return s

    def filter_tags(self,htmlstr):
        re_cdata=re.compile('//<!\[CDATA\[.*//\]\]>',re.DOTALL)
        re_script=re.compile('<\s*script[^>]*>.*?<\s*/\s*script\s*>',re.DOTALL|re.I)
        re_style=re.compile('<\s*style[^>]*>.*?<\s*/\s*style\s*>',re.DOTALL|re.I)
        re_textarea = re.compile('<\s*textarea[^>]*>.*?<\s*/\s*textarea\s*>',re.DOTALL|re.I)
        re_br=re.compile('<br\s*?/?>')
        re_h=re.compile('</?\w+.*?>',re.DOTALL)
        re_comment=re.compile('<!--.*?-->',re.DOTALL)
        s=re_cdata.sub('',htmlstr)
        s=re_script.sub('',s)
        s=re_style.sub('',s)
        s = re_textarea.sub('',s)
        s=re_br.sub('',s)
        s=re_h.sub('',s)
        s=re_comment.sub('',s)
        s = re.sub('\\t','',s)
        zhPattern = re.compile(u'([\u4e00-\u9fa5]+) +')
        s = re.sub(zhPattern,r'\1',s)
        zhPattern = re.compile(u' +([\u4e00-\u9fa5]+)')
        s = re.sub(zhPattern,r'\1',s)
        s=self.replaceCharEntity(s)
        return s




def getcurTimestr():
    return time.strftime(  '%Y-%m-%d %X', time.localtime() )



def ValidateTime( pubtimeint ):
    nowt = datetime.datetime.now()
    limit = datetime.datetime(nowt.year,nowt.month,nowt.day,23,59,59)
    if pubtimeint > int(time.mktime(limit.timetuple())):
        return None
    return pubtimeint
        

parserTable = None
def initCSSParser():
    _parserTable = None
    with open('./gspider_parser.json') as data_file:
        _parserTable = json.load(data_file)
    return _parserTable

def IndexParser( paras ):
    html = paras['html']
    url = paras['url']
    date = paras['date']
    title = paras['title']
    item = {}
    item['parser'] = 'Index'
    try:
        item['title'] = title
        item['pdate'] = parseGoogleDate(date)
        item['pdate'] = ValidateTime( item['pdate'] )
        item['content'] = None
        return item
    except Exception , e:
        print e
        return item

def RDparsetime(timestr):
    try:
        if timestr:
            pubtime = dateparser.parse(timestr)
            if pubtime==None:
                if not u' ' in timestr:
                    pubtime = dateutil.parser.parse(timestr,fuzzy=True)
                else:
                    day = timestr.split(u' ',1)[0]
                    temp = timestr.split(u' ',1)[1]
                    dateru = u''
                    if u'時間前' == temp or u'小時前' == temp:
                        dateru = day + u' час назад'
                    else:
                        if u'分前' == temp or u'分鐘前' == temp:
                            dateru = day + u' минут назад'
                    pubtime = dateparser.parse(dateru)
            else:
                pass
            if pubtime:
                pubtimeint = int(time.mktime(pubtime.timetuple()))
                return pubtimeint
            else:
                return 0
        else:
            return 0
    except BaseException as e:
        print e
        return 0


def parseGoogleDate(datestr):
    dateint = 0
    try:
        pubtime =  dateparser.parse( datestr )
        if pubtime:
            dateint = int(time.mktime(pubtime.timetuple()))
    except Exception , e:
        print e
        print "parse google date failed " + datestr
        dateint = 0
    if dateint == 0:
        dateint =  RDparsetime( datestr )
    return dateint


def CSSParser( paras ):
    html = paras['html']
    url = paras['url']
    item = {}
    item['parser'] = 'CSS'
    try: 
        url_ext = tldextract.extract(url).domain
        parser = getsafedictvalue(parserTable, url_ext+"/parser", None)
        cnname = getsafedictvalue(parserTable, url_ext + "/name", "")
        if parser is None:
            return item

        linkurl = url
        docrsp = doc(html,url)
        pubtimeint = 0
        pubtimetxt=''
        for CSS in parser:
            contraw = docrsp(CSS["content"]).remove("a").remove("script").remove("style")
            if contraw == None:
                continue
            item['content'] = contraw.text()
            item['title'] = docrsp(CSS["title"]).text()
            pubtimetxt = docrsp(CSS["date"]).text()
            item['pdate'] = parsedate(pubtimetxt)
            if (len( item['content']) > 0) and (len(item['title']) > 0) and (item['pdate'] > 0):
                break;
                
        if contraw:
            cleaner = clean.Cleaner(page_structure=True)
            showcont = cleaner.clean_html(contraw.remove_attr('id').remove_attr('class').wrapAll('<div></div>').html())
            showcont = re.sub(r'id=".*?"|class=".*?"', '', showcont)
            showcont = re.sub(r'[\s+]*?>', '>', showcont)
            showcont = showcont.replace("\n", "").replace("\t", "").replace("<div>", "").replace("</div>", "")
            item['showcontent'] = showcont
            item['pdate'] = ValidateTime( item['pdate'] )

        return item
    except Exception , e:
        print e
        return item
 


def NewspaperParser( paras ):
    html = paras['html']
    url = paras['url']
    item = {}
    item['parser'] = 'Newspaper'
    try:
        docrsp = doc(html,url)
        config = Config()
        config.fetch_images = False
        first_article = Article(url=url, config=config)
        first_article.download(docrsp.html())
        first_article.parse()
        item['title'] = first_article.title
        pubtime = first_article.publish_date
        if pubtime:
            pubtimeint = int(time.mktime(pubtime.timetuple()))
            item['pdate'] = pubtimeint
        item['content'] = first_article.text
        item['pdate'] = ValidateTime( item['pdate'] )
        item['showcontent'] = item['content'].replace("\n", "<br/>")
        return item

    except Exception , e:
        print e
        return item

def CXParser( paras ):
    html = paras['html']
    url = paras['url']
    parserTable = {}
    item = {}
    try:
        item['parser'] = 'CX'
        docrsp = doc(html,url)
        cx = cx_extractor()
        test_html = docrsp.html() #cx.getHtml(response.url)
        s = cx.filter_tags(test_html)
        item['content'] = cx.getText(s)
        item['showcontent'] = item['content'].replace("\n", "<br/>")
        item['pdate'] = None
        return item
    except Exception , e:
        print e
        return item

def ArticleDateParser( paras ):
    html = paras['html']
    url = paras['url']
    parserTable = {}
    item = {}
    try:
        item['parser'] = 'ArticleDate'
        docrsp = doc(html,url)
        pubdate = articleDateExtractor.extractArticlePublishedDate(url, docrsp.html())
        if pubdate:
            item['pdate'] = int(time.mktime(pubdate.timetuple()))
            item['pdate'] = ValidateTime( item['pdate'] )
        return item
    except Exception , e:
        print e
        return item

paperChain = [   CSSParser , NewspaperParser , CXParser , ArticleDateParser ,IndexParser ]


def parseTDC( paras ):
    retItem={
       }
    for parser in paperChain:
        item = parser( paras )
        if item.get('title') != None and len(item.get('title')) > 0 and retItem.get('title') == None :
            retItem['title']={'parser':item['parser'], 'value' : item['title'] }

        if item.get('content') != None and len(item.get('content')) > 0 and retItem.get('content') == None :
            retItem['content'] = {'parser':item['parser'], 'value' : item['content'] }

        if item.get('pdate') != None and item.get('pdate') > 0 and retItem.get('pdate') == None :
            retItem['pdate'] = {'parser':item['parser'], 'value' : item['pdate'] }
            
        if item.get('showcontent') != None and len(item.get('showcontent')) > 0 and retItem.get('showcontent') == None :
            retItem['showcontent'] = {'parser':item['parser'], 'value' : item['showcontent'] }
        
        if retItem.get('pdate') != None and retItem.get('title') != None and retItem.get('content') != None:
            return retItem
    return retItem
