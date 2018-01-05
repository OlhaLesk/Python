#!/usr/bin/env python3
import cgi
import logging
import os

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qsl, urlsplit


#Create custom HTTPRequestHandler class
class CustomHTTPRequestHandler(BaseHTTPRequestHandler):

    def _set_response(self, length=None):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        if length:
            self.send_header("Content-Length", str(length))
        self.end_headers()

    def server_info(self):
        """Display some information about the server.

        127.0.0.1:80/info
        """
        message = '<!DOCTYPE html>' \
                  '<html>' \
                  '  <head>' \
                  '    <title>Server Info</title>' \
                  '  </head>' \
                  '  <body>' \
                  '    <table>' \
                  '      <tbody>' \
                  '        <tr>' \
                  '          <td>client_address</td>' \
                  '          <td>%s</td>' \
                  '        </tr>' \
                  '        <tr>' \
                  '          <td>method</td>' \
                  '          <td>%s</td>' \
                  '        </tr>' \
                  '        <tr>' \
                  '          <td>command</td>' \
                  '          <td>%s</td>' \
                  '        </tr>' \
                  '        <tr>' \
                  '          <td>path</td>' \
                  '          <td>%s</td>' \
                  '        </tr>' \
                  '        <tr>' \
                  '          <td>server_version</td>' \
                  '          <td>%s</td>' \
                  '        </tr>' \
                  '        <tr>' \
                  '          <td>sys_version</td>' \
                  '          <td>%s</td>' \
                  '        </tr>' \
                  '      </tbody>' \
                  '    </table>' \
                  '    <input type="button" onclick="history.back()" ' \
                  '           value="Back" />' \
                  '  </body>' \
                  '</html>' % (self.client_address,
                               self.command,
                              self.headers,
                               self.path,
                               self.server_version,
                               self.sys_version)

        length = len(message)
        self._set_response(length)
        self.wfile.write(bytes(message, 'utf8'))

    #handle GET command
    def do_GET(self):
        logging.info("\nMethod: %s,\nPath: %s\nHeaders:\n%s\n",
                     str(self.command), str(self.path), str(self.headers))
        script_directory = os.path.dirname(os.path.realpath(__file__))
        try:
            if self.path.endswith('.html'):
                #open requested file
                f = open(script_directory + '/template/' + self.path)

                self._set_response()

                #send file content to client
                self.wfile.write(bytes(f.read(), 'utf8'))
                f.close()
                return
            elif self.path == '/':
                f = open(script_directory + '/template/' + 'get_vs_post.html')

                self._set_response()
                self.wfile.write(bytes(f.read(), 'utf8'))
                f.close()
                return
            elif self.path == '/info' or self.path == '/info/':
                self.server_info()
                return
        except IOError:
            self.send_error(404, 'file not found')

        params = dict(parse_qsl(urlsplit(self.path).query))
        self.form_response(params.get('firstname'), params.get('lastname'))

    #handle POST command
    def do_POST(self):
        logging.info("\nMethod: %s,\nPath: %s\nHeaders:\n%s\n",
                     str(self.command), str(self.path), str(self.headers))
#        length = int(self.headers.get('Content-length', 0))
#        data = self.rfile.read(length).decode()
#        print(length)
#        print(data)
        form = cgi.FieldStorage(fp=self.rfile,
                                headers=self.headers,
                                environ={'REQUEST_METHOD': 'POST',
                                         'CONTENT_TYPE': self.headers[
                                             'Content-Type'],
                                         })
        self.form_response(form.getfirst('firstname'),
                           form.getfirst('lastname'))

    def form_response(self, firstname, lastname):
        if not firstname:
            firstname = ''
        if not lastname:
            lastname = ''
        response = '<!DOCTYPE html>' \
                   '<html>' \
                   '  <head>' \
                   '    <title>%s form input</title>' \
                   '  </head>' \
                   '  <body>' \
                   '    <h1>Hello %s %s!</h1>' \
                   '    <input type="button" onclick="history.back()" ' \
                   '           value="Back" />' \
                   '  </body>' \
                   '</html>' % (str(self.command), firstname, lastname)
        length = len(response)
        self._set_response(length)
        self.wfile.write(bytes(response, 'utf8'))


def run(*, port=None):
    logging.basicConfig(level=logging.INFO)

    server_address = None
    #ip and port of server
    if port:
        server_address = ('127.0.0.1', port)
    else:
        #by default http server port is 80
        server_address = ('127.0.0.1', 80)
    httpd = HTTPServer(server_address, CustomHTTPRequestHandler)
    logging.info('Starting http server...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logging.info('Stopping http server...\n')
    httpd.server_close()

if __name__ == '__main__':
    from sys import argv
    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()

