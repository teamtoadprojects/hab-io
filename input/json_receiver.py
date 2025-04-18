
import asyncio
from datetime import datetime
import json
import http.server

from core import PluginBase, Payload, PayloadType


class RequestHandler(http.server.BaseHTTPRequestHandler):

    def __init__(self, core, logger):
        self.core = core
        self.logger = logger

    def __call__(self, *args, **kwds):
        return super().__init__(*args, **kwds)

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        json_message = json.loads(post_data)
        self.logger.info("Received JSON message", json_message=json_message)
        payload = Payload(
            type=PayloadType.TELEMETRY,
            callsign=json_message.get("callsign"),
            payload_id=json_message.get("payload_id"),
            time=datetime.strptime(json_message.get("time", "00:00:00"), "%H:%M:%S"),  # "time":"12:34:56
            latitude=float(json_message.get("latitude", 0.0)),
            longitude=float(json_message.get("longitude", 0.0)),
            altitude=float(json_message.get("altitude", 0.0)),
            temperature=json_message.get("temperature"),
            sats=json_message.get("sats"),
            battery=json_message.get("battery"),
            pressure=json_message.get("pressure"),
            speed=float(json_message.get("speed", 0.0)),
            ascent_rate=json_message.get("ascent_rate"),
            other_fields=json_message.get("other_fields"),
        )
        asyncio.run(self.core.receive_payload(payload))
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()


class json_receiver(PluginBase):

    def start_http_server(self):
        server_address = ('', self.config["port"])
        handler = RequestHandler(self.core, self.logger)
        httpd = http.server.HTTPServer(server_address, handler)
        httpd.serve_forever()

    async def start(self):
        await super().start()

        self.loop.run_in_executor(None, self.start_http_server)
