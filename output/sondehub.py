from sondehub.amateur import Uploader

from core import PluginBase, Payload


class sondehub(PluginBase):

    async def start(self):
        await super().start()
        self.uploader = Uploader(
            self.core.config["core"]["callsign"],
            developer_mode=self.config["developer_mode"],
        )

    async def output(self, payload: Payload):
        self.logger.info("Outputting payload", payload=payload)

        self.uploader.add_telemetry(
            payload.callsign,
            payload.time.strftime("%H:%M:%S"),
            payload.latitude,
            payload.longitude,
            payload.altitude,
            frame=payload.payload_id,
            sats=payload.sats,
            batt=payload.battery,
            pressure=payload.pressure,
            temp=payload.temperature,
        )
