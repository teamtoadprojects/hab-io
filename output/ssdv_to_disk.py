from pathlib import Path
import subprocess

from core import PluginBase, Payload, PayloadType


class ssdv_to_disk(PluginBase):

    async def start(self):
        await super().start()
        self.payload_types = [PayloadType.SSDV]

    async def output(self, payload: Payload):
        self.logger.info("Outputting payload", payload=payload)

        root_name = f"{payload.callsign}_{payload.payload_id}"
        filename = f"{root_name}.ssdv"
        directory = Path(self.config["directory"])
        full_output_path = directory / filename
        with open(full_output_path, 'ab') as output_file:
            data = bytes.fromhex(payload.other_fields["ssdv"])
            output_file.write(data)
            output_file.flush()

        subprocess.call(
            f"/ssdv/ssdv -d {directory / filename} {directory / root_name}.jpg",
            shell=True,
        )

        self.logger.info("Wrote SSDV packet to disk", filename=filename)
