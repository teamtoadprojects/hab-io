import asyncio
from core import PluginBase
import random
import string
import time
from datetime import datetime

from core import Payload, PayloadType


class demo_input(PluginBase):

    packet_count = 0
    callsign = ""

    def __init__(self, config, core, loop):
        super().__init__(config, core, loop)
        self.callsign = self.generate_callsign()

    def generate_callsign(self):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    def get_current_time(cls):
        return datetime.now().strftime("%H:%M:%S")

    def emit_packet(self):
        while True:
            time.sleep(self.config["interval"])
            self.packet_count += 1
            # Simulate emitting a packet
            payload = Payload(
                type=PayloadType.TELEMETRY,
                callsign=self.callsign,
                payload_id=self.packet_count,
                time=self.get_current_time(),
                latitude=round(random.uniform(-90.0, 90.0), 2),
                longitude=round(random.uniform(-180.0, 180.0), 2),
                altitude=round(random.uniform(0.0, 10000.0), 2),
                temperature=round(random.uniform(-50.0, 50.0), 2),
                sats=random.randint(0, 20),
                battery=round(random.uniform(0.0, 100.0), 2),
                pressure=round(random.uniform(900.0, 1100.0), 2),
                speed=round(random.uniform(0.0, 300.0), 2),
                ascent_rate=round(random.uniform(-10.0, 10.0), 2),
                recieved_at=datetime.now(),
            )

            asyncio.run(self.core.receive_payload(payload))

    async def start(self):
        await super().start()
        self.loop.run_in_executor(None, self.emit_packet)
        print("Demo plugin started with config: {}".format(self.config))


    def run(self):
        super().run()
        print("Demo plugin running with config: {}".format(self.config))
