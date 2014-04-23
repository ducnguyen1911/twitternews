from crawler import settings
from news_processing import news_cluster

__author__ = 'duc07'


import os
import cgi
import sys
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import cPickle as pickle

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
                ls_topics = pickle.load( open( "topics.p", "rb" ) )

                print '1'
                for topic in ls_topics:
                    self.wfile.write('<p>Topic: ' + topic[0] + '</p>')
                    self.wfile.write('<p>Topic Geo Center: ' + str(topic[2][0]) + ' : ' + str(topic[2][1]) + '</p>')
                    self.wfile.write('<p>Topic Score: ' + str(topic[3]) + '--</p>')
                    for tweet in topic[1]:
                        self.wfile.write('<p> Tweet: ' + self.encode(tweet['text']) + '</p>')
                    self.wfile.write('<p>------------------------------------</p>')

        def encode(self, text):
            """
            For printing unicode characters to the console.
            """
            return text.encode('utf-8')

def main():
        try:
                server = HTTPServer(('',8080),customHTTPServer)
                print 'server started at port 8080'
                server.serve_forever()
        except KeyboardInterrupt:
                server.socket.close()

if __name__=='__main__':
        main()