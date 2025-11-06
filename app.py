from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.request import urlopen
import os

API_HOST = os.getenv("API_HOST", "cmtx-api-public")
API_PORT = int(os.getenv("API_PORT", "8080"))

INDEX = """<!doctype html>
<html><head><meta charset="utf-8"><title>CMTX Web</title></head>
<body style="font-family:sans-serif">
  <h2>CMTX Web (Frontend)</h2>
  <p>Consulta API → DATA → Mongo (PVC). Credenciales en Secret.</p>
  <button onclick="fetch('/call').then(r=>r.text()).then(t=>document.getElementById('out').innerText=t)">Consultar</button>
  <pre id="out"></pre>
</body></html>"""

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ["/", "/index.html"]:
            b = INDEX.encode()
            self.send_response(200); self.send_header("Content-Type","text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b); return
        if self.path == "/call":
            try:
                with urlopen(f"http://{API_HOST}:{API_PORT}/hello", timeout=5) as r:
                    data = r.read()
                self.send_response(200); self.end_headers(); self.wfile.write(b"WEB ▶ " + data)
            except Exception as e:
                self.send_response(500); self.end_headers(); self.wfile.write(f"front error: {e}".encode())
            return
        if self.path == "/health":
            self.send_response(200); self.end_headers(); self.wfile.write(b"ok"); return
        self.send_response(404); self.end_headers()

if __name__ == "__main__":
    HTTPServer(("", 8080), H).serve_forever()