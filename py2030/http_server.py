import threading, httplib, socket
from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler

class MyRequestHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        if self.path.endswith('config.yaml'):
            return '/config/config.yaml'

        return SimpleHTTPRequestHandler.translate_path(self, path)

class HttpServer(threading.Thread):
    def __init__(self, options={}):
        threading.Thread.__init__(self)
        self.options = options
        self.url = ""
        self.port = self.options['port'] if 'port' in self.options else 2031 # 8888
        self.kill = False

    def stop(self):
        if not self.isAlive():
            return

        self.kill = True

        print 'Sending dummy HTTP request to stop blocking HTTP server...'
        try:
            connection = httplib.HTTPConnection('127.0.0.1', self.port)
            connection.request('HEAD', '/')
            connection.getresponse()
        except socket.error:
            pass

    def run(self):
        print 'Starting HTTP server on ', (self.url, self.port)
        self.httpd = HTTPServer((self.url, self.port), MyRequestHandler)
        # self.httpd.serve_forever()
        # self.httpd.server_activate()
        while not self.kill:
            try:
                self.httpd.handle_request()
            except:
                print 'http exception'

        print 'Closing HTTP server ', (self.url, self.port)
        self.httpd.server_close()
