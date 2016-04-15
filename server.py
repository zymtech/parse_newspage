# -*- coding: utf-8 -*-
import tornado.ioloop
import tornado.web
import click
from parserlogic import *
from parserservicelog import *


class parserHandler(tornado.web.RequestHandler):
    def get(self):
        try:
            self.write("not available yet")
        except Exception as e:
            print e

    def post(self,*args,**kwargs):
        try:
            jsonstr = self.request.body
            data = json.loads(jsonstr)
            paras = {
                'html' : data['htmltext'],
                'url' : data['url'],
                'date' : data['idate'],
                'title' : data['title'],
                'lang': data['lang']
            }
            item = parseTDC(paras)
            self.set_header('Content-Type','application/javascript')
            self.write(item)
            self.finish()
            pslogger = psdblogger('x9.ddns.net',27001)
            pslogger.proccess(item,data['url'],data['idate'],data['lang'])
        except Exception as e:
            print e


class application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/parser/v1',parserHandler)
        ]
        tornado.web.Application.__init__(self,handlers)


@click.command()
@click.option('--port',default = 8888, help = 'Port that application listens')
def main(port):
    app = application()
    app.listen(port)
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    try:
        main()
    except BaseException as e:
        print e