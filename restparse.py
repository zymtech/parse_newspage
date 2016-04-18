import json
import requests
import ast


class serviceparser:
    """serviceparser implemented in Python"""
    __serviceurl = 'http://127.0.0.1:27023/parser/'
    __version = 'v1'

    def __init__(self, __serviceurl, __version):
        self.__serviceurl = __serviceurl
        self.__version = __version

    def restparse(self, url, htmltext, date, title, lang):
        parserurl = self.__serviceurl + self.__version
        data = {
            'url' : url,
            'htmltext': htmltext,
            'idate': date,
            'title': title,
            'lang': lang
        }
        jdata = json.dumps(data)
        headers = {'content-type':'application/json'}
        try:
            tornadoresponse = requests.post(parserurl, data=jdata, headers=headers)
            item = ast.literal_eval(tornadoresponse.content)
            print "restparse: ", item
            item['content']['value'] = item['content']['value'].decode('unicode_escape')
            item['title']['value'] = item['title']['value'].decode('unicode_escape')
            item['showcontent']['value'] = item['showcontent']['value'].decode('unicode_escape')
            return item
        except BaseException as e:
            print e
            return None
