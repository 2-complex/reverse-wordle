from http.server import HTTPServer, BaseHTTPRequestHandler
import re
import requests
import json
import html
import importlib
import guesser

class WebServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        good_paths = set([
            "/jquery/jquery-ui.min.css",
            "/jquery/jquery-ui.min.js",
            "/jquery/jquery.min.js",
            "/wordle.css",
            "/wordle.js",
            "/wordle.html"
        ])

        if self.path == "" or self.path == "/":
            self.send_response(200)
            self.send_header("content-type", "text/html")
            self.end_headers()
            self.wfile.write(open("main.html").read().encode("utf-8"))
        elif self.path in good_paths:
            self.send_response(200)
            self.send_header("content-type", "text/html")
            self.end_headers()
            self.wfile.write(open(self.path[1:]).read().encode("utf-8"))
        else:
            self.send_error(404, "File not found: {}".format(self.path))

    def do_POST(self):
        if self.path == "/next":
            importlib.reload(guesser)
            length = int(self.headers.get('content-length'))
            post_data_bytes = self.rfile.read(length)
            post_data_str = post_data_bytes.decode('utf-8')

            try:
                received_json = json.loads(post_data_str)
            except json.JSONDecodeError:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'Invalid JSON received')
                return

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('X-Custom-Header', 'MyValue')
            self.end_headers()

            guess = guesser.guess(received_json["guesses"])

            self.wfile.write((json.dumps(guess)+"\n").encode("utf-8"))
            return

        self.send_error(500, "ERROR {}".format(self.path))

def main():
    import sys
    if len(sys.argv) < 2:
        print("Wrong number of arguments, please specify a port")
        return

    port = 0
    try:
        port = int(sys.argv[1])
    except:
        print("Port given did not convert to integer, please supply a port.. like 8080..")
        return

    while True:
        try:
            print("Serving on port {}".format(port))
            server = HTTPServer(('', port), WebServerHandler)
            server.serve_forever()
        except KeyboardInterrupt:
            print("Keybaord interrupt, closing socket, bailing")
            server.socket.close()
            return
        except:
            print("Unexpected exception raised, restarting")
            print()

if __name__ == '__main__':
    main()



