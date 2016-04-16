# -*- encoding: utf-8 -*-
import pymongo
import time
import tldextract
import datetime
from getsafedictvalue import getsafedictvalue


class psdblogger():
    """ dblogger of parser service"""
    def __init__(self,host='127.0.0.1',port=27001):
        client = pymongo.MongoClient(host,port)
        logdb = client.logdb
        self.clog = logdb.pslog

    def insertlog(self , url , item, lang, spidername='pyspider', issuccessful=False ):
        domain = tldextract.extract(url).registered_domain
        print url,domain,
        self.clog.insert({
            "url" : url,
            "domain" : domain,
            "title" : item['title']['value'],
            "pdate" : item['pdate']['value'],
            "content" : item['content']['value'],
            "showcontent":item['showcontent']['value'],
            "parsertype":{
                "title":item['title']['parser'],
                "content":item['content']['parser'],
                'pdate': item['pdate']['parser'],
                "showcontent":item['showcontent']['parser']
            },
            "spider":spidername,
            "lang": lang,
            "issuccessful":issuccessful,
            "crawltime": datetime.datetime.utcnow()
        }
        )

    def proccess(self,TDCItem,url,date,lang):
        contraw = getsafedictvalue(TDCItem,'content/value','')
        title = getsafedictvalue(TDCItem,'title/value','')
        pubtimeint = getsafedictvalue(TDCItem,'pdate/value',0)
        contrawhtml = getsafedictvalue(TDCItem,'showcontent/value','')

        if (len(contraw) <= 0) or (len(title) <= 0) or (pubtimeint == ''):  #失败
            msg = ""
            if (len(contraw) <= 0 ):
                msg = "content"
            elif (len(title) <= 0):
                msg = "title"
            else:
                msg = "pubtime"
            print "  --> write to db failed :  ",msg , "not complete"
            self.insertlog(url = url ,item = TDCItem , issuccessful = False,lang = lang)
        else:
            self.insertlog(url = url , item = TDCItem,issuccessful = True,lang = lang)
            print "        --> write to hdb ok ..."


