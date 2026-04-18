import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from datetime import datetime, timezone
from backend.src.api import (
    get_sample_payload,
    batch_enrich_leads,
    build_value_signal_summary,
    clamp_value_score,
    classify_value_band,
    prioritize_leads_by_enrichment_gap,
)

class Handler(BaseHTTPRequestHandler):
    def _send(self, code, payload):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode('utf-8'))

    def _read_body(self):
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            return None
        body = self.rfile.read(content_length)
        return json.loads(body.decode('utf-8'))

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

    def do_POST(self):
        if self.path == '/enrich':
            try:
                body = self._read_body()
                if not body:
                    self._send(400, {'error': 'missing_body'})
                    return
                
                leads = body.get('leads', [])
                config = body.get('config')
                
                result = batch_enrich_leads(leads, config)
                result['processed_at'] = datetime.now(timezone.utc).isoformat()
                self._send(200, result)
                return
            except json.JSONDecodeError:
                self._send(400, {'error': 'invalid_json'})
                return
            except Exception as e:
                self._send(500, {'error': 'internal_error', 'message': str(e)})
                return

        if self.path == '/v1/value-score':
            try:
                body = self._read_body()
                if not body:
                    self._send(400, {'error': 'missing_body'})
                    return
                account_id = body.get('accountId')
                score = body.get('score')
                if account_id is None or score is None:
                    self._send(400, {'error': 'missing_fields', 'required': ['accountId', 'score']})
                    return
                result = build_value_signal_summary(account_id, score)
                result['processed_at'] = datetime.now(timezone.utc).isoformat()
                self._send(200, result)
                return
            except Exception as e:
                self._send(500, {'error': 'internal_error', 'message': str(e)})
                return

        if self.path == '/v1/leads/prioritize':
            try:
                body = self._read_body()
                if not body:
                    self._send(400, {'error': 'missing_body'})
                    return
                leads = body.get('leads', [])
                weights = body.get('weights')
                result = prioritize_leads_by_enrichment_gap(leads, weights)
                self._send(200, {'prioritized': result, 'total': len(result), 'processed_at': datetime.now(timezone.utc).isoformat()})
                return
            except Exception as e:
                self._send(500, {'error': 'internal_error', 'message': str(e)})
                return

        self._send(404, {'error':'not_found','path':self.path})


def run(host="0.0.0.0", port=None):
    port = port or int(os.environ.get("PORT", 8000))
    server = HTTPServer((host, port), Handler)
    print(f'Starting lf-openalex-enrichment-mvp on {host}:{port}')
    server.serve_forever()

if __name__ == '__main__':
    run()
