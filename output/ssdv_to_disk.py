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

        result = subprocess.run(
            f"/ssdv/ssdv -d {directory / filename} {directory / root_name}.jpg",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        self.logger.info("Wrote SSDV packet to disk", filename=filename)

        self.logger.info(
            "SSDV conversion result",
            stdout=result.stdout,
            stderr=result.stderr,
        )
        # Check if the conversion was successful
        if result.returncode != 0:
            self.logger.error(
                "SSDV conversion failed",
                error=result.stderr,
                filename=filename,
            )           

