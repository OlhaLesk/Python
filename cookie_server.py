#!/usr/bin/env python3
#
# An HTTP server that remembers your name (in a cookie)

from html import escape as html_escape
from http import cookies
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs


form = ('<!DOCTYPE html>'
        '<title>What is your name?</title>'
        '<p>'
        '  {}'
        '</p>'
        '<form method="POST">'
        '  <label>What\'s your name again?'
        '    <input type="text" name="username">'
        '  </label>'
        '  <br>'
        '  <button type="submit">Tell me!</button>'
        '</form>')


class NameHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('Content-length', 0))
        data = self.rfile.read(length).decode()
        username = None
        try:
            username = parse_qs(data)["username"][0]
        except (KeyError, cookies.CookieError) as err:
            message = "Please, input your name!"
            print(err)

            self.send_response(202)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            mesg = form.format(message)
            self.wfile.write(mesg.encode())
            return


        c = cookies.SimpleCookie()
        c['username'] = username
        c['username']['domain'] = 'localhost'
        c['username']['max-age'] = 60

        self.send_response(303)  # redirect via GET
        self.send_header('Location', '/')
        self.send_header('Set-Cookie', c['username'].OutputString())
        self.end_headers()

    def do_GET(self):
        message = "I don't know yout name yet!"

        if 'cookie' in self.headers:
            try:
                c = cookies.SimpleCookie(self.headers['cookie'])
                name = c['username'].value

                message = "Hi, " + html_escape(name)
            except (KeyError, cookies.CookieError) as err:
                message = "I'm not sure of your name!"
                print(err)

        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        mesg = form.format(message)
        self.wfile.write(mesg.encode())

if __name__ == '__main__':
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, NameHandler)
    httpd.serve_forever()

