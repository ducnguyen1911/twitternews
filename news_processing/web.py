from crawler import settings
from news_processing import news_cluster

__author__ = 'duc07'


import os
import cgi
import sys
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

class customHTTPServer(BaseHTTPRequestHandler):
        def do_GET(self):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write('<HTML><body>')
                self.write_content()
                self.wfile.write('</body></HTML>')
                return

        def do_POST(self):
                global rootnode
                ctype,pdict = cgi.parse_header(self.headers.getheader('Content-type'))
                if ctype == 'multipart/form-data':
                        query = cgi.parse_multipart(self.rfile, pdict)
                self.send_response(301)
                self.end_headers()
                self.wfile.write('Post!')

        def write_content(self):
                print 'write content'
                tweet_bulk = news_cluster.lda_train()
                print '1'
                for [topic, ls_tweets] in tweet_bulk:
                    self.wfile.write('<p>Topic ------------------' + topic + '------------------</p>')
                    for tweet in ls_tweets:
                        self.wfile.write('<p> Tweet: ' + tweet + '</p>')


def main():
        try:
                server = HTTPServer(('',8080),customHTTPServer)
                print 'server started at port 8080'
                server.serve_forever()
        except KeyboardInterrupt:
                server.socket.close()

if __name__=='__main__':
        main()