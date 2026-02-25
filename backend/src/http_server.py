from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from datetime import datetime, timezone
from backend.src.api import get_sample_payload

class Handler(BaseHTTPRequestHandler):
    def _send(self, code, payload):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode('utf-8'))

    def do_GET(self):
        if self.path == '/health':
            self._send(200, {'status':'ok','service':'lf-openalex-enrichment-mvp'})
            return
        if self.path == '/sample':
            payload=get_sample_payload()
            payload['transport']='http'
            payload['generatedAtHttp']=datetime.now(timezone.utc).isoformat()
            self._send(200,payload)
            return
        self._send(404, {'error':'not_found','path':self.path})


def run(host='0.0.0.0', port=8000):
    server = HTTPServer((host, port), Handler)
    print(f'Starting lf-openalex-enrichment-mvp on {host}:{port}')
    server.serve_forever()

if __name__ == '__main__':
    run()
