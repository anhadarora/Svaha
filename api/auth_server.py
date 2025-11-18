import http.server
import socketserver
import webbrowser
from urllib.parse import urlparse, parse_qs

class AuthServer:
    def __init__(self, port=8080):
        self.port = port
        self.httpd = None
        self.request_token = None

    def start(self, login_url):
        handler = self.get_handler()
        socketserver.TCPServer.allow_reuse_address = True
        self.httpd = socketserver.TCPServer(("", self.port), handler)
        print(f"Serving at port {self.port}")
        webbrowser.open(login_url)
        self.httpd.handle_request() # Handle one request and then stop

    def get_handler(self):
        auth_server_instance = self
        class RequestHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                parsed_path = urlparse(self.path)
                query_params = parse_qs(parsed_path.query)
                if 'request_token' in query_params:
                    auth_server_instance.request_token = query_params['request_token'][0]
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(b"<html><body><h1>Login successful. You can close this window.</h1></body></html>")
                    auth_server_instance.httpd.server_close()
                else:
                    self.send_response(400)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(b"<html><body><h1>Login failed.</h1></body></html>")
        return RequestHandler
