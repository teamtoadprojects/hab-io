import asyncio

import serial

from core import PluginBase, Payload


class serial_receiver(PluginBase):

    def __init__(self, config, core, loop):
        super().__init__(config, core, loop)
        self.serial_port = serial.Serial(config["port"], config["baudrate"])

    async def start(self):
        await super().start()
        self.loop.run_in_executor(None, self.read_serial)

    def read_serial(self):
        while True:
            line = self.serial_port.readline().decode().strip()
            if not line.startswith("$$"):
                continue
            self.logger.info("Received line from serial port", line=line)
            payload = Payload(
                callsign=line.split(",")[0],
                payload_id=line.split(",")[1],
                time=line.split(",")[2],
                latitude=line.split(",")[3],
                longitude=line.split(",")[4],
                altitude=line.split(",")[5],
                temperature=line.split(",")[6],
                sats=line.split(",")[7],
                battery=line.split(",")[8],
                pressure=line.split(",")[9],
                speed=line.split(",")[10],
                ascent_rate=None,
                other_fields={
                    "checksum": line.split(",")[11],
                }
            )
            asyncio.run(self.core.receive_payload(payload))

    def run(self):
        self.logger.info("Running plugin with config", config=self.config)
