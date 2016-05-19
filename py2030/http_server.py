import threading, httplib, socket
from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler

class MyRequestHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        # print '[MyRequestHandler] translate_path:', path
        if path.endswith('config.yaml'):
            #     print 'assumed config.yaml'
            return SimpleHTTPRequestHandler.translate_path(self, '/config/config.yaml')

        return SimpleHTTPRequestHandler.translate_path(self, path)

class HttpServer(threading.Thread):
    def __init__(self, options={}):
        threading.Thread.__init__(self)
        self.options = options
        self.url = ""
        self.port = self.options['port'] if 'port' in self.options else 2040 # 8888
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

    def _get_host(self):
        if 'host_info' in self.options:
            return self.options['host_info']['ip']

        return socket.gethostbyname(socket.gethostname())

    def version_url(self, version):
        return "http://{0}:{1}/{2}".format(self._get_host(), self.port, 'data/py2030-' + version + '.tar.gz')

    # def config_url(self):
    #     return "http://{0}:{1}/{2}".format(self._get_host(), self.port, 'config/config.yaml')
