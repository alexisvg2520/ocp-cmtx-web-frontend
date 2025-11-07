from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
import os, socket, contextlib

API_HOST = os.getenv("API_HOST", "cmtx-api-public")
API_PORT = int(os.getenv("API_PORT", "8080"))
API_URL  = f"http://{API_HOST}:{API_PORT}/hello"

INDEX = """<!doctype html>
<html><head><meta charset="utf-8"><title>CMTX Web</title></head>
<body style="font-family:sans-serif">
  <h2>CMTX Web (Frontend)</h2>
  <p>Consulta API → DATA → Mongo (PVC). Credenciales en Secret.</p>
  <button onclick="fetch('/call').then(r=>r.text()).then(t=>document.getElementById('out').innerText=t)">Consultar</button>
  <pre id="out"></pre>
</body></html>"""

class Handler(BaseHTTPRequestHandler):
    def _diagnose_upstream(self) -> str:
        lines = [f"API_URL={API_URL}"]
        try:
            infos = socket.getaddrinfo(API_HOST, API_PORT, proto=socket.IPPROTO_TCP)
            uniq = sorted({f"{info[4][0]}:{info[4][1]}" for info in infos})
            lines.append("DNS ✔ " + ", ".join(uniq))
        except socket.gaierror as e:
            lines.append(f"DNS ✖ {e}")
        try:
            with contextlib.closing(socket.create_connection((API_HOST, API_PORT), timeout=2)):
                lines.append("TCP CONNECT ✔")
        except OSError as e:
            lines.append(f"TCP CONNECT ✖ {e}")
        return "\n".join(lines)

    def _write(self, status: int, text: str, ctype: str = "text/plain; charset=utf-8"):
        body = text.encode("utf-8", "replace")
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._write(200, INDEX, "text/html; charset=utf-8")
            return

        if self.path == "/call":
            try:
                req = Request(API_URL, headers={"User-Agent": "cmtx-web-frontend"})
                with urlopen(req, timeout=5) as resp:
                    payload_bytes = resp.read()
                payload_text = payload_bytes.decode("utf-8", "replace")
                self._write(200, f"WEB ▶ {payload_text}")
            except HTTPError as e:
                self._write(502, f"front error: upstream HTTP {e.code}")
            except URLError as e:
                self._write(502, f"front error: upstream unreachable ({e.reason})")
            except Exception as e:
                self._write(500, f"front error: {e}")
            return

        if self.path == "/health":
            self._write(200, "ok")
            return

        if self.path == "/diag":
            self._write(200, self._diagnose_upstream())
            return

        self._write(404, "not found")

if __name__ == "__main__":
    port = 8080
    print(f"cmtx-web-frontend listening on {port}, calling {API_URL}")
    HTTPServer(("", port), Handler).serve_forever()
