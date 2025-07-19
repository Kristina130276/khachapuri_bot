from http.server import BaseHTTPRequestHandler, HTTPServer

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive")

if __name__ == "__main__":
    port = 8080
    print(f"Fake web server running on port {port}")
    server = HTTPServer(("", port), SimpleHandler)
    server.serve_forever()