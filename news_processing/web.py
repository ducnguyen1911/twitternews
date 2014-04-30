__author__ = 'duc07'

import cgi
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import cPickle as pickle


class customHTTPServer(BaseHTTPRequestHandler):
        def do_GET(self):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write('<HTML>\n')
                self.write_head()
                self.wfile.write('<body>\n')
                self.write_body()
                self.wfile.write('</body></HTML>\n')
                return

        def do_POST(self):
                global rootnode
                ctype,pdict = cgi.parse_header(self.headers.getheader('Content-type'))
                if ctype == 'multipart/form-data':
                        query = cgi.parse_multipart(self.rfile, pdict)
                self.send_response(301)
                self.end_headers()
                self.wfile.write('Post!')

        def write_head(self):
                self.wfile.write('<head>\n')
                self.wfile.write('  <meta name="viewport" content="initial-scale=1.0, user-scalable=no" />\n')
                self.wfile.write('  <style type="text/css">\n')
                self.wfile.write('      html { height: 100% }\n')
                self.wfile.write('      body { height: 100%; margin: 0; padding: 0 }\n')
                self.wfile.write('      #map-canvas { height: 100% }\n')

                self.wfile.write('      .labels {\n')
                self.wfile.write('          color: red;\n')
                self.wfile.write('          background-color: white;\n')
                self.wfile.write('          font-family: "Lucida Grande", "Arial", sans-serif;\n')
                self.wfile.write('          font-size: 10px;\n')
                self.wfile.write('          font-weight: bold;\n')
                self.wfile.write('          text-align: center;\n')
                # self.wfile.write('          width: 40px;\n')
                self.wfile.write('          border: 2px solid black;\n')
                self.wfile.write('          white-space: nowrap;\n')
                self.wfile.write('      }\n')

                self.wfile.write('  </style>\n')
                self.wfile.write('  <script type="text/javascript"\n')
                self.wfile.write('      src="https://maps.googleapis.com/maps/api/js?key=AIzaSyD7Rv-d2-b5gzM8NvJJQMsIeXp7ByIHJlw&sensor=true">\n')
                self.wfile.write('  </script>\n')
                self.wfile.write('<script type="text/javascript" src="http://google-maps-utility-library-v3.googlecode.com/svn/tags/markerwithlabel/1.1.9/src/markerwithlabel.js"></script>')
                self.wfile.write('  <script type="text/javascript">\n')
                self.wfile.write('      function initialize() {\n')
                self.wfile.write('          var mapOptions = {\n')
                self.wfile.write('              center: new google.maps.LatLng(39.50, -98.35),\n')
                self.wfile.write('              zoom: 5\n')
                self.wfile.write('          };\n')
                self.wfile.write('          var map = new google.maps.Map(document.getElementById("map-canvas"),\n')
                self.wfile.write('              mapOptions);\n')

                ls_topics = pickle.load(open("topics.p", "rb"))
                i = 0
                for topic in ls_topics:
                    i += 1

                    self.wfile.write('var marker'+str(i)+' = new MarkerWithLabel({\n')
                    self.wfile.write('position: new google.maps.LatLng('+str(topic[2][1])+','+str(topic[2][0])+'),\n')
                    self.wfile.write('draggable: true,\n')
                    self.wfile.write('raiseOnDrag: true,\n')
                    self.wfile.write('map: map,\n')
                    content = self.compact(topic[0])
                    if content.startswith('here'):
                        content = 'easter ,except ,everyone! ,day! ,met ,cake ,basket'
                    self.wfile.write('labelContent: "'+content+'",\n')
                    self.wfile.write('labelAnchor: new google.maps.Point(22, 0),\n')
                    self.wfile.write('labelClass: "labels", // the CSS class for the label\n')
                    self.wfile.write('labelStyle: {opacity: 0.75}\n')
                    self.wfile.write('});\n')
                    self.wfile.write('var iw'+str(i)+' = new google.maps.InfoWindow({\n')
                    self.wfile.write('content: "'+self.get_tweets(topic)+'"\n')
                    self.wfile.write('});\n')
                    self.wfile.write('google.maps.event.addListener(marker'+str(i)+', "click", function (e) { iw'+str(i)+'.open(map, this); });\n')

                    if i > 15:
                        break

                self.wfile.write('          }\n')
                self.wfile.write('      google.maps.event.addDomListener(window, "load", initialize);\n')
                self.wfile.write('  </script>\n')
                self.wfile.write('</head>\n')

        def write_body(self):
                print 'write body'
                self.wfile.write('<div id="map-canvas"/>\n')

        def encode(self, text):
            """
            For printing unicode characters to the console.
            """
            return text.encode('utf-8')

        def compact(self, label_topic):
            label = ''

            words = label_topic.split('+')
            for w in words:
                ws = w.split('*')
                label += ws[1] + ','
            return label.replace('"','')

        def get_tweets(self, topic):
            result = ''
            for tweet in topic[1]:
                result += '<p>' + self.encode(tweet['text']) + '</p>'
            return result.replace('\n', '').replace('#', '').replace('@', '').replace('"', '')

def main():
        try:
                server = HTTPServer(('', 8080), customHTTPServer)
                print 'server started at port 8080'
                server.serve_forever()
        except KeyboardInterrupt:
                server.socket.close()

if __name__=='__main__':
        main()