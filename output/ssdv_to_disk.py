from pathlib import Path

from core import PluginBase, Payload, PayloadType


class ssdv_to_disk(PluginBase):

    async def start(self):
        await super().start()
        self.payload_types = [PayloadType.SSDV]

    async def output(self, payload: Payload):
        self.logger.info("Outputting payload", payload=payload)

        filename = f"{payload.callsign}_{payload.payload_id}.ssdv"
        full_output_path = Path(self.config["directory"]) / filename
        with open(full_output_path, 'ab') as output_file:
            data = bytes.fromhex(payload.other_fields["ssdv"])
            output_file.write(data)
            output_file.flush()

        self.logger.info("Wrote SSDV packet to disk", filename=filename)
