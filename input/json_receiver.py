import asyncio
import json
import http.server

import aiohttp
import concurrent.futures

from core import PluginBase, Payload


class json_receiver(PluginBase):

    def handle_client(self):

        payload = Payload(
            callsign=json_message.get("callsign"),
            payload_id=json_message.get("payload_id"),
            time=json_message.get("time"),
            latitude=json_message.get("latitude"),
            longitude=json_message.get("longitude"),
            altitude=json_message.get("altitude"),
            temperature=json_message.get("temperature"),
            sats=json_message.get("sats"),
            battery=json_message.get("battery"),
            pressure=json_message.get("pressure"),
            speed=json_message.get("speed"),
            ascent_rate=json_message.get("ascent_rate"),
            other_fields=json_message.get("other_fields"),
        )
        self.core.receive_payload(payload)

    def start_http_server(self):
        server_address = ('', self.config["port"])
        httpd = http.server.HTTPServer(server_address, http.server.SimpleHTTPRequestHandler)
        httpd.serve_forever()

    async def start(self):
        await super().start()

        self.loop.run_in_executor(None, self.start_http_server)
