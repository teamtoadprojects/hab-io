import asyncio
import json
import serial
import serial_asyncio
import time

from core import PluginBase


class pico_display_output(PluginBase):

    sending = False
    queue = asyncio.Queue()

    async def start(self):
        await super().start()
        try:
            self.loop.run_in_executor(None, self.send, self.queue)
        except Exception as e:
            self.logger.error("Failed to start Pico Display Output plugin", error=str(e))
        self.logger.info("Pico Display Output plugin started with config", config=self.config)


    def send(self, queue):
        self.logger.info("Starting send queue")
        try:
            serial_port = serial.Serial(
                self.config["port"],
                baudrate=self.config["baudrate"],
            )

            self.logger.info("Serial port opened", port=self.config["port"], baudrate=self.config["baudrate"])

            while True:
                if not self.sending:
                    self.sending = True
                    try:
                        payload = queue.get_nowait()
                    except asyncio.QueueEmpty:
                        self.sending = False
                        time.sleep(0.1)
                        continue
                    self.logger.info("Sending data to Pico Display")
                    update_data = {
                        "packet_type": payload.type.value,
                        "callsign": payload.callsign,
                        "packet_number": payload.payload_id,
                        "latitude": payload.latitude,
                        "longitude": payload.longitude,
                        "altitude": payload.altitude,
                        "speed": payload.speed,
                        "time": payload.recieved_at.strftime("%H:%M:%S"),
                        "frequency": "433Mhz",
                    }

                    output_data = json.dumps(update_data).encode() + b"\n"
                    serial_port.write(output_data)
                    serial_port.flush()
                    self.logger.info("Data sent to Pico Display", data=update_data)

                    # If we don't read the response, the serial port will block
                    # as the buffer fills up
                    while (serial_port.in_waiting > 0):
                        response = serial_port.readline().decode().strip()
                        self.logger.info("Received response from Pico Display", response=response)

                    self.sending = False
        except Exception as e:
            self.logger.error("Failed to send data to Pico Display", error=str(e))
            self.sending = False        

    async def output(self, payload):
        self.logger.info("Outputting payload", payload=payload)

        self.queue.put_nowait(payload)
