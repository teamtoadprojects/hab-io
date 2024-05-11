from dataclasses import dataclass, asdict
import json
from datetime import time

import asyncudp

from core import PluginBase, Payload


@dataclass
class OziPayload:
    callsign: str
    latitude: float
    longitude: float
    altitude: float
    speed: float
    time: str
    heading: int = -1
    type: str = "PAYLOAD_SUMMARY"


    def __init__(self, payload: Payload):
        self.callsign = payload.callsign
        self.latitude = payload.latitude
        self.longitude = payload.longitude
        self.altitude = payload.altitude
        self.speed = payload.speed
        self.time = payload.time.strftime("%H:%M:%S") if payload.time else time().strftime("%H:%M:%S")

    def to_json(self):
        return json.dumps(asdict(self))

class ozijson(PluginBase):

    async def start(self):
        await super().start()
        self.udp = await asyncudp.create_socket(remote_addr=(self.config["host"], self.config["port"]))

    async def output(self, payload):
        self.logger.info("Outputting payload", payload=payload)
        ozi_payload = OziPayload(payload)
        udp_packet = ozi_payload.to_json().encode()
        self.logger.info("Sending packet", packet=udp_packet)
        self.udp.sendto(udp_packet)
