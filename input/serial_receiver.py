import asyncio
from datetime import datetime

import serial

from core import PluginBase, Payload


class serial_receiver(PluginBase):

    async def start(self):
        await super().start()
        try:
            self.serial_port = serial.Serial(
                self.config["port"], self.config["baudrate"]
            )
            self.loop.run_in_executor(None, self.read_serial)
        except Exception as e:
            self.logger.error("Failed to open serial port", error=str(e))

    def read_serial(self):
        while True:
            line = self.serial_port.readline().decode().strip()
            if not line.startswith("$$"):
                continue
            self.logger.info("Received line from serial port", line=line)
            payload = Payload(
                callsign=line.split(",")[0].removeprefix("$$"),
                payload_id=line.split(",")[1],
                time=datetime.strptime(line.split(",")[2], "%H:%M:%S"),
                latitude=float(line.split(",")[3]) if line.split(",")[3] else 0.0,
                longitude=float(line.split(",")[4]) if line.split(",")[4] else 0.0,
                altitude=float(line.split(",")[5]) if line.split(",")[5] else 0.0,
                temperature=float(line.split(",")[6]) if line.split(",")[6] else 0.0,
                sats=int(line.split(",")[7]) if line.split(",")[7] else 0,
                battery=float(line.split(",")[8]) if line.split(",")[8] else 0.0,
                pressure=float(line.split(",")[9]) if line.split(",")[9] else 0.0,
                speed=float(line.split(",")[10]) if line.split(",")[10] else 0.0,
                ascent_rate=None,
                other_fields={
                    "checksum": line.split(",")[11],
                },
            )
            asyncio.run(self.core.receive_payload(payload))

    def run(self):
        self.logger.info("Running plugin with config", config=self.config)
