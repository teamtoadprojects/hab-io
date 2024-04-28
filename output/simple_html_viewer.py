import asyncio
import json
import http.server

from core import PluginBase, Payload

class RequestHandler(http.server.BaseHTTPRequestHandler):

    def __init__(self, core, logger):
        self.core = core
        self.logger = logger
        self.payloads = []

    def __call__(self, *args, **kwds):
        return super().__init__(*args, **kwds)

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"<html><head><title>Simple Payload Viewer</title></head>")
        self.wfile.write(b"<body><h1>Simple Payload Viewer</h1>")
        self.wfile.write(b"<table border=1>")
        self.wfile.write(b"<tr><th>Callsign</th><th>Payload ID</th><th>Time</th><th>Latitude</th><th>Longitude</th><th>Altitude</th><th>Temperature</th><th>Sats</th><th>Battery</th><th>Pressure</th><th>Speed</th><th>Ascent Rate</th><th>Other Fields</th></tr>")
        for payload in self.payloads:
            self.wfile.write(b"<tr>")
            self.wfile.write(f"<td>{payload.callsign}</td>".encode())
            self.wfile.write(f"<td>{payload.payload_id}</td>".encode())
            self.wfile.write(f"<td>{payload.time}</td>".encode())
            self.wfile.write(f"<td>{payload.latitude}</td>".encode())
            self.wfile.write(f"<td>{payload.longitude}</td>".encode())
            self.wfile.write(f"<td>{payload.altitude}</td>".encode())
            self.wfile.write(f"<td>{payload.temperature}</td>".encode())
            self.wfile.write(f"<td>{payload.sats}</td>".encode())
            self.wfile.write(f"<td>{payload.battery}</td>".encode())
            self.wfile.write(f"<td>{payload.pressure}</td>".encode())
            self.wfile.write(f"<td>{payload.speed}</td>".encode())
            self.wfile.write(f"<td>{payload.ascent_rate}</td>".encode())
            self.wfile.write(f"<td>{payload.other_fields}</td>".encode())
            self.wfile.write(b"</tr>")
        self.wfile.write(b"</table>")
        self.wfile.write(b"</body></html>")
        self.wfile.flush()


class simple_html_viewer(PluginBase):

    async def output(self, payload: Payload):
        self.handler.payloads.append(payload)

    def start_http_server(self):
        server_address = ('', self.config["port"])
        self.handler = RequestHandler(self.core, self.logger)
        httpd = http.server.HTTPServer(server_address, self.handler)
        httpd.serve_forever()

    async def start(self):
        await super().start()

        self.loop.run_in_executor(None, self.start_http_server)
