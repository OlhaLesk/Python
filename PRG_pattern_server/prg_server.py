#!/usr/bin/env python3
#
# An HTTP server that has just a message board.

import os
import threading

from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from urllib.parse import parse_qs


memory = []

form = '''<!DOCTYPE html>
            <title>Message Board</title>
            <form method="POST">
              <textarea name="message"></textarea>
              <br>
              <button type="submit">Post it!</button>
             </form>
             <pre>
{}
             </pre>'''


class MessageHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        length = int(self.headers.get('Content-length', 0))

        data = self.rfile.read(length).decode()
        message = parse_qs(data)["message"][0]

        # Escape HTML tags in the message so users can't break world+dog.
        message = message.replace("<", "&lt;")

        memory.append(message)

        self.send_response(303)  # redirect via GET
        self.send_header('Location', '/')
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()

        mesg = form.format("\n".join(memory))
        self.wfile.write(mesg.encode())


class ThreadHTTPServer(ThreadingMixIn, HTTPServer):
    "This is an HTTPServer that supports thread-based concurrency."
    pass


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    server_address = ('', port)
    httpd = ThreadHTTPServer(server_address, MessageHandler)
    httpd.serve_forever()

