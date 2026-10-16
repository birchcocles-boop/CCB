"""Calyx Command Bridge v0.5.0 HTTPS-proxied receiver."""
import json, os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from ccb_http import handle as sandbox_handle
from ccb_auth import authorized as admin_authorized
from ccb_devices import issue as issue_device

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / 'web'
HOST = '127.0.0.1'
PORT = int(os.environ.get('CCB_PORT', '8765'))

class Handler(BaseHTTPRequestHandler):
    def _send(self, code, payload, cookie=None):
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        if cookie:
            self.send_header('Set-Cookie', cookie)
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ('/', '/index.html', '/console.html'):
            body = (WEB / ('console.html' if path == '/console.html' else 'index.html')).read_bytes()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(body)
        elif path == '/api/health':
            self._send(200, {'ok': True, 'name': 'CCB LAN', 'version': '0.5.0'})
        else:
            self._send(404, {'error': 'Not found'})

    def do_POST(self):
        if urlparse(self.path).path == '/api/device/pair':
            from ccb_pair import handle as pair_handle
            code, result, cookie = pair_handle(self)
            return self._send(code, result, cookie)

        if urlparse(self.path).path == '/api/sandbox/run':
            code, result = sandbox_handle(self)
            return self._send(code, result)
        return self._send(404, {'error': 'Not found'})

if __name__ == '__main__':
    print(f'CCB LAN: http://{HOST}:{PORT}')
    try:
        ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
    except KeyboardInterrupt:
        print('\nCCB stopped.')
