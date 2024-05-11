from dataclasses import dataclass
from time import time

import asyncudp

from core import PluginBase


class OziPayload:
    type: str = "PAYLOAD_SUMMARY"
    callsign: str
    latitude: float
    longitude: float
    altitude: float
    speed: float
    heading: int = -1
    time: time


    def __init__(self, payload):
        self.callsign = payload.callsign
        self.latitude = payload.latitude
        self.longitude = payload.longitude
        self.altitude = payload.altitude
        self.speed = payload.speed
        self.time = payload.time

class ozijson(PluginBase):

    async def output(self, payload):
        self.logger.info("Outputting payload", payload=payload)
