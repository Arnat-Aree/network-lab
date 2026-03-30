import http.server
import threading
import json

class HealthHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args): pass
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status":"ok","service":"upload","server":"ServerA"}).encode())
    def do_POST(self): self.do_GET()

class GatewayHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args): pass
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status":"processed","gateway":"ServerA"}).encode())
    def do_GET(self): self.do_POST()

def run(port, handler):
    httpd = http.server.HTTPServer(('0.0.0.0', port), handler)
    httpd.serve_forever()

for port, handler in [(8000, HealthHandler),(8001, HealthHandler),(8002, HealthHandler),(9000, GatewayHandler)]:
    t = threading.Thread(target=run, args=(port, handler), daemon=True)
    t.start()

print("ServerA services started on ports 8000,8001,8002,9000")
import time
while True: time.sleep(60)
