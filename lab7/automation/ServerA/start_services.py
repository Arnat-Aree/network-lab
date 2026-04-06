import http.server
import json
import psycopg2
import redis
import sys
import time

SERVER_NAME = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

def init_db():
    for _ in range(10):
        try:
            conn = psycopg2.connect(
                dbname="network_db", user="admin", password="password", host="172.20.10.12", connect_timeout=3
            )
            cur = conn.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS access_logs (id SERIAL PRIMARY KEY, server_name VARCHAR(50), timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP);")
            conn.commit()
            cur.close()
            conn.close()
            print("PostgreSQL initialized successfully.")
            return True
        except Exception as e:
            print(f"Waiting for Postgres... {e}")
            time.sleep(3)
    return False

redis_client = redis.Redis(host='172.20.10.11', port=6379, db=0, socket_connect_timeout=3)

class AppHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args): pass
    def do_GET(self):
        try:
            redis_client.incr('request_count')
            count = int(redis_client.get('request_count'))
            
            conn = psycopg2.connect(dbname="network_db", user="admin", password="password", host="172.20.10.12")
            cur = conn.cursor()
            cur.execute("INSERT INTO access_logs (server_name) VALUES (%s)", (SERVER_NAME,))
            conn.commit()
            
            cur.execute("SELECT COUNT(*) FROM access_logs")
            db_count = cur.fetchone()[0]
            cur.close()
            conn.close()

            response = {
                "server": SERVER_NAME,
                "status": "success",
                "redis_total_requests": count,
                "postgres_total_logs": db_count
            }
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e), "server": SERVER_NAME}).encode())

if __name__ == "__main__":
    init_db()
    server_address = ('0.0.0.0', 8000)
    httpd = http.server.HTTPServer(server_address, AppHandler)
    print(f"{SERVER_NAME} running on port 8000")
    httpd.serve_forever()
